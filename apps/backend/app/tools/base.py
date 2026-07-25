from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """Contrato uniforme de uma tool chamável pelo LLM.

    Cada tool declara `name`, `description` e `input_schema` (JSON Schema) e
    implementa `execute`, recebendo os argumentos já desserializados.
    """

    name: str
    description: str
    input_schema: dict[str, Any]

    @abstractmethod
    def execute(self, arguments: dict[str, Any]) -> Any:
        """Executa a tool com os argumentos fornecidos e retorna o resultado."""
        raise NotImplementedError

    def schema(self) -> dict[str, Any]:
        """Representação da tool para montagem do payload ao LLM."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }
