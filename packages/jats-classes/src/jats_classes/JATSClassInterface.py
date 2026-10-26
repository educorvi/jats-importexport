import abc


class JATSClassInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def to_xml(self) -> str:
        raise NotImplementedError
