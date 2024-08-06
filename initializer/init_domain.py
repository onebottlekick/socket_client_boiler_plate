from client_socket.service.client_socket_service_impl import ClientSocketServiceImpl
from command_analyzer.service.command_analyzer_service_impl import CommandAnalyzerServiceImpl
from custom_protocol.entity.default_protocol import DefaultProtocolNumber
from custom_protocol.service.custom_protocol_service_impl import CustomProtocolServiceImpl
from dice.service.dice_service_impl import DiceServiceImpl
from receiver.service.receiver_service_impl import ReceiverServiceImpl
from transmitter.service.transmitter_service_impl import TransmitterServiceImpl


class DomainInitializer:
    @staticmethod
    def initDiceDomain():
        DiceServiceImpl.getInstance()

    @staticmethod
    def initCustomProtocolDomain():
        customProtocolService = CustomProtocolServiceImpl.getInstance()
        diceService = DiceServiceImpl.getInstance()

        # 디폴트 프로토콜 등록을 여기서 했음
        customProtocolService.registerCustomProtocol(
            DefaultProtocolNumber.DICE_ROLL_JUST_FOR_TEST,
            diceService.rollDice
        )

        customProtocolService.registerCustomProtocol(
            DefaultProtocolNumber.DICE_LIST_JUST_FOR_TEST,
            diceService.diceList
        )

    @staticmethod
    def initClientSocketDomain():
        ClientSocketServiceImpl.getInstance()

    @staticmethod
    def initReceiverDomain():
        ReceiverServiceImpl.getInstance()

    @staticmethod
    def initCommandAnalyzerDomain():
        CommandAnalyzerServiceImpl.getInstance()

    @staticmethod
    def initTransmitterDomain():
        TransmitterServiceImpl.getInstance()

    @staticmethod
    def initEachDomain():
        DomainInitializer.initDiceDomain()
        DomainInitializer.initCustomProtocolDomain()

        DomainInitializer.initClientSocketDomain()
        DomainInitializer.initReceiverDomain()
        DomainInitializer.initCommandAnalyzerDomain()
        DomainInitializer.initTransmitterDomain()


