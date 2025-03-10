"""
Data models for the Veda Platform API.
"""

from typing import Dict, List, Any, Optional, Union, TypeVar, Generic


class ValueItem:
    """
    Represents a value item in the Veda data model.
    """
    
    def __init__(
        self,
        data: Any,
        type_: str,
        lang: Optional[str] = None
    ):
        """
        Initialize a new value item.
        
        Args:
            data: The value data.
            type_: The data type.
            lang: Optional language code.
        """
        self.data = data
        self.type = type_
        self.lang = lang
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ValueItem':
        """
        Create a ValueItem instance from a dictionary.
        
        Args:
            data: Dictionary representation of a value item.
            
        Returns:
            A new ValueItem instance.
        """
        return cls(
            data=data.get("data"),
            type_=data.get("type"),
            lang=data.get("lang")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the ValueItem to a dictionary.
        
        Returns:
            Dictionary representation of the ValueItem.
        """
        result = {
            "data": self.data,
            "type": self.type
        }
        
        if self.lang:
            result["lang"] = self.lang
        
        return result


class Individual:
    """
    Represents an individual in the Veda data model.
    """
    
    def __init__(self, uri: str, properties: Optional[Dict[str, List[ValueItem]]] = None):
        """
        Initialize a new individual.
        
        Args:
            uri: The unique identifier (URI) of the individual.
            properties: Optional dictionary of properties.
        """
        self.uri = uri
        self.properties = properties or {}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Individual':
        """
        Create an Individual instance from a dictionary.
        
        Args:
            data: Dictionary representation of an individual.
            
        Returns:
            A new Individual instance.
        """
        uri = data.get("@")
        properties = {}
        
        for key, value in data.items():
            if key != "@":
                if isinstance(value, list):
                    properties[key] = [ValueItem.from_dict(item) for item in value]
        
        return cls(uri=uri, properties=properties)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Individual to a dictionary.
        
        Returns:
            Dictionary representation of the Individual.
        """
        result = {"@": self.uri}
        
        for key, values in self.properties.items():
            result[key] = [value.to_dict() for value in values]
        
        return result
    
    def get_property(self, key: str) -> List[ValueItem]:
        """
        Get the values of a property.
        
        Args:
            key: The property key.
            
        Returns:
            List of ValueItem instances for the property.
        """
        return self.properties.get(key, [])
    
    def get_first_value(self, key: str) -> Optional[Any]:
        """
        Get the data value of the first item of a property.
        
        Args:
            key: The property key.
            
        Returns:
            Data value or None if the property doesn't exist or is empty.
        """
        values = self.get_property(key)
        return values[0].data if values else None
    
    def set_property(self, key: str, values: List[Union[ValueItem, Dict[str, Any]]]) -> None:
        """
        Set a property with multiple values.
        
        Args:
            key: The property key.
            values: List of ValueItem instances or dictionaries.
        """
        self.properties[key] = []
        
        for value in values:
            if isinstance(value, ValueItem):
                self.properties[key].append(value)
            elif isinstance(value, dict):
                self.properties[key].append(ValueItem.from_dict(value))
    
    def add_value(self, key: str, data: Any, type_: str, lang: Optional[str] = None) -> None:
        """
        Add a value to a property.
        
        Args:
            key: The property key.
            data: The value data.
            type_: The data type.
            lang: Optional language code.
        """
        if key not in self.properties:
            self.properties[key] = []
        
        self.properties[key].append(ValueItem(data=data, type_=type_, lang=lang))
    
    def remove_property(self, key: str) -> None:
        """
        Remove a property.
        
        Args:
            key: The property key.
        """
        if key in self.properties:
            del self.properties[key]
    
    def set_value(self, key: str, data: Any, type_: str, lang: Optional[str] = None) -> None:
        """
        Устанавливает одно значение свойства, удаляя все предыдущие значения.
        
        Args:
            key: Ключ свойства.
            data: Данные значения.
            type_: Тип данных.
            lang: Опциональный код языка.
        """
        self.properties[key] = [ValueItem(data=data, type_=type_, lang=lang)]
    
    def replace_value(self, key: str, old_data: Any, new_data: Any, type_: str, lang: Optional[str] = None) -> bool:
        """
        Заменяет существующее значение на новое, если старое значение существует.
        
        Args:
            key: Ключ свойства.
            old_data: Старые данные для замены.
            new_data: Новые данные.
            type_: Тип данных.
            lang: Опциональный код языка.
            
        Returns:
            True если значение было заменено, False в противном случае.
        """
        if key not in self.properties:
            return False
        
        for i, value_item in enumerate(self.properties[key]):
            if value_item.data == old_data:
                self.properties[key][i] = ValueItem(data=new_data, type_=type_, lang=lang)
                return True
        
        return False
    
    def remove_value(self, key: str, data: Any) -> bool:
        """
        Удаляет конкретное значение из свойства.
        
        Args:
            key: Ключ свойства.
            data: Данные для удаления.
            
        Returns:
            True если значение было удалено, False в противном случае.
        """
        if key not in self.properties:
            return False
        
        original_length = len(self.properties[key])
        self.properties[key] = [item for item in self.properties[key] if item.data != data]
        
        return len(self.properties[key]) < original_length
    
    def remove_predicate(self, predicate: str) -> bool:
        """
        Удаляет предикат из набора предикатов.
        
        Args:
            predicate: Предикат (ключ свойства) для удаления.
            
        Returns:
            True если предикат был удален, False если он не существовал.
        """
        if predicate in self.properties:
            del self.properties[predicate]
            return True
        return False
