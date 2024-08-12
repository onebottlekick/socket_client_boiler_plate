import json
import socket
import ssl
import threading
from time import sleep

import select

from critical_section.manager import CriticalSectionManager
from custom_protocol.entity.custom_protocol import CustomProtocolNumber
from receiver.repository.receiver_repository_impl import ReceiverRepositoryImpl
from receiver.service.receiver_service import ReceiverService
from request_generator.generator import RequestGenerator
from utility.color_print import ColorPrinter


class ReceiverServiceImpl(ReceiverService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__receiverRepository = ReceiverRepositoryImpl.getInstance()

            cls.__instance.__criticalSectionManager = CriticalSectionManager.getInstance()

            cls.__instance.__receiverLock = threading.Lock()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def requestToInjectClientSocket(self, clientSocket):
        self.__receiverRepository.injectClientSocket(clientSocket)

    def requestToInjectReceiverAnalyzerChannel(self, ipcReceiverAnalyzerChannel):
        self.__receiverRepository.injectReceiverAnalyzerChannel(ipcReceiverAnalyzerChannel)

    def __blockToAcquireSocket(self):
        if self.__criticalSectionManager.getClientSocket() is None:
            return True

        return False

    def requestToReceiveCommand(self):
        while self.__blockToAcquireSocket():
            ColorPrinter.print_important_message("Receiver: Try to get SSL Socket")
            sleep(0.5)

        ColorPrinter.print_important_message("Receiver 구동 성공!")

        # clientSocketObject = self.__receiverRepository.getClientSocket()
        clientSocket = self.__criticalSectionManager.getClientSocket()
        ColorPrinter.print_important_data("requestToReceiveCommand()", clientSocket)
        clientSocketObject = clientSocket.getSocket()

        while True:
            try:
                with self.__receiverLock:
                    readyToRead, _, inError = select.select([clientSocketObject], [], [], 0.5)

                    if not readyToRead:
                        continue

                    receivedData = self.__receiverRepository.receive(clientSocketObject)

                if not receivedData:
                    self.__receiverRepository.closeConnection()
                    break

                try:
                    dictionaryData = json.loads(receivedData)
                    ColorPrinter.print_important_data("dictionaryData", dictionaryData)

                except json.JSONDecodeError as e:
                    ColorPrinter.print_important_data("JSON Decode Error", str(e))
                    continue

                protocolNumber = dictionaryData.get("command")
                ColorPrinter.print_important_data("protocolNumber", protocolNumber)

                data = dictionaryData.get("data", {})
                ColorPrinter.print_important_data("data", data)

                if protocolNumber is not None:
                    ColorPrinter.print_important_data("received protocol",
                                                      f"Protocol Number: {protocolNumber}, Data: {data}")

                    # 요청을 처리합니다.
                    protocol = CustomProtocolNumber(protocolNumber)
                    request = RequestGenerator.generate(protocol, data)
                    ColorPrinter.print_important_data("processed request", f"{request}")

                    self.__receiverRepository.sendDataToCommandAnalyzer(request)

            except ssl.SSLError as sslError:
                ColorPrinter.print_important_data("receive 중 SSL Error", str(sslError))
                self.__receiverRepository.closeConnection()
                break

            except BlockingIOError:
                pass

            except socket.error as socketException:
                if socketException.errno == socket.errno.EAGAIN == socket.errno.EWOULDBLOCK:
                    ColorPrinter.print_important_message("문제 없음")
                    sleep(0.5)

                else:
                    ColorPrinter.print_important_message("수신 중 에러")

            except (socket.error, BrokenPipeError) as exception:
                ColorPrinter.print_important_message("Broken Pipe")
                self.__receiverRepository.closeConnection()
                break

            except Exception as exception:
                ColorPrinter.print_important_data("Receiver 정보", str(exception))

            finally:
                sleep(0.5)
