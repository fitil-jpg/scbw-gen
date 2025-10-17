#!/usr/bin/env python3
"""
Validation System
Система валідації конфігурацій з детальними повідомленнями про помилки
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import json
import yaml

LOG = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Рівні валідації"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationSeverity(Enum):
    """Серйозність помилки"""
    CRITICAL = "critical"    # Критична помилка, валідація не пройшла
    HIGH = "high"           # Серйозна помилка, але можна продовжити
    MEDIUM = "medium"       # Попередження
    LOW = "low"            # Інформаційне повідомлення


@dataclass
class ValidationIssue:
    """Проблема валідації"""
    field_path: str
    message: str
    level: ValidationLevel
    severity: ValidationSeverity
    expected_value: Optional[Any] = None
    actual_value: Optional[Any] = None
    suggestion: Optional[str] = None
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Результат валідації"""
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    errors: List[ValidationIssue] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self):
        # Розподілити проблеми за типами
        for issue in self.issues:
            if issue.level == ValidationLevel.ERROR:
                self.errors.append(issue)
            elif issue.level == ValidationLevel.WARNING:
                self.warnings.append(issue)
        
        # Підрахувати підсумки
        self.summary = {
            "total_issues": len(self.issues),
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "critical": len([i for i in self.issues if i.severity == ValidationSeverity.CRITICAL]),
            "high": len([i for i in self.issues if i.severity == ValidationSeverity.HIGH]),
            "medium": len([i for i in self.issues if i.severity == ValidationSeverity.MEDIUM]),
            "low": len([i for i in self.issues if i.severity == ValidationSeverity.LOW])
        }
        
        # Визначити загальну валідність
        self.is_valid = len(self.errors) == 0


class ValidationRule:
    """Правило валідації"""
    
    def __init__(self, field_path: str, 
                 validator: Callable[[Any], bool],
                 message: str,
                 level: ValidationLevel = ValidationLevel.ERROR,
                 severity: ValidationSeverity = ValidationSeverity.HIGH,
                 required: bool = False,
                 data_type: Optional[type] = None,
                 min_value: Optional[Union[int, float]] = None,
                 max_value: Optional[Union[int, float]] = None,
                 allowed_values: Optional[List[Any]] = None,
                 pattern: Optional[str] = None,
                 custom_validator: Optional[Callable[[Any], ValidationIssue]] = None):
        self.field_path = field_path
        self.validator = validator
        self.message = message
        self.level = level
        self.severity = severity
        self.required = required
        self.data_type = data_type
        self.min_value = min_value
        self.max_value = max_value
        self.allowed_values = allowed_values
        self.pattern = pattern
        self.custom_validator = custom_validator
    
    def validate(self, data: Dict[str, Any]) -> Optional[ValidationIssue]:
        """Валідувати поле"""
        value = self._get_nested_value(data, self.field_path)
        
        # Перевірка обов'язковості
        if self.required and value is None:
            return ValidationIssue(
                field_path=self.field_path,
                message=f"Поле '{self.field_path}' є обов'язковим",
                level=ValidationLevel.ERROR,
                severity=ValidationSeverity.CRITICAL,
                expected_value="не null",
                actual_value=value,
                suggestion="Додайте відсутнє поле або встановіть значення за замовчуванням"
            )
        
        if value is None:
            return None  # Необов'язкове поле може бути None
        
        # Кастомна валідація
        if self.custom_validator:
            return self.custom_validator(value)
        
        # Базові перевірки
        issues = []
        
        # Перевірка типу
        if self.data_type and not isinstance(value, self.data_type):
            issues.append(ValidationIssue(
                field_path=self.field_path,
                message=f"Поле '{self.field_path}' повинно бути типу {self.data_type.__name__}",
                level=ValidationLevel.ERROR,
                severity=ValidationSeverity.HIGH,
                expected_value=self.data_type.__name__,
                actual_value=type(value).__name__,
                suggestion=f"Змініть тип даних на {self.data_type.__name__}"
            ))
        
        # Перевірка числових значень
        if isinstance(value, (int, float)):
            if self.min_value is not None and value < self.min_value:
                issues.append(ValidationIssue(
                    field_path=self.field_path,
                    message=f"Поле '{self.field_path}' повинно бути >= {self.min_value}",
                    level=ValidationLevel.ERROR,
                    severity=ValidationSeverity.MEDIUM,
                    expected_value=f">= {self.min_value}",
                    actual_value=value,
                    suggestion=f"Збільшіть значення до {self.min_value} або більше"
                ))
            
            if self.max_value is not None and value > self.max_value:
                issues.append(ValidationIssue(
                    field_path=self.field_path,
                    message=f"Поле '{self.field_path}' повинно бути <= {self.max_value}",
                    level=ValidationLevel.ERROR,
                    severity=ValidationSeverity.MEDIUM,
                    expected_value=f"<= {self.max_value}",
                    actual_value=value,
                    suggestion=f"Зменшіть значення до {self.max_value} або менше"
                ))
        
        # Перевірка дозволених значень
        if self.allowed_values and value not in self.allowed_values:
            issues.append(ValidationIssue(
                field_path=self.field_path,
                message=f"Поле '{self.field_path}' повинно бути одним з: {self.allowed_values}",
                level=ValidationLevel.ERROR,
                severity=ValidationSeverity.MEDIUM,
                expected_value=self.allowed_values,
                actual_value=value,
                suggestion=f"Використайте одне з дозволених значень: {', '.join(map(str, self.allowed_values))}"
            ))
        
        # Перевірка за регулярним виразом
        if self.pattern and isinstance(value, str):
            if not re.match(self.pattern, value):
                issues.append(ValidationIssue(
                    field_path=self.field_path,
                    message=f"Поле '{self.field_path}' не відповідає шаблону",
                    level=ValidationLevel.ERROR,
                    severity=ValidationSeverity.MEDIUM,
                    expected_value=f"відповідає шаблону: {self.pattern}",
                    actual_value=value,
                    suggestion=f"Виправте формат відповідно до шаблону: {self.pattern}"
                ))
        
        # Загальна валідація
        if not self.validator(value):
            issues.append(ValidationIssue(
                field_path=self.field_path,
                message=self.message,
                level=self.level,
                severity=self.severity,
                actual_value=value,
                suggestion="Перевірте правильність значення"
            ))
        
        return issues[0] if issues else None
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Отримати значення з вкладеної структури"""
        keys = field_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                index = int(key)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            else:
                return None
        
        return current


class ValidationSchema:
    """Схема валідації"""
    
    def __init__(self, name: str, version: str = "1.0"):
        self.name = name
        self.version = version
        self.rules: List[ValidationRule] = []
        self.custom_validators: List[Callable[[Dict[str, Any]], List[ValidationIssue]]] = []
    
    def add_rule(self, rule: ValidationRule) -> 'ValidationSchema':
        """Додати правило валідації"""
        self.rules.append(rule)
        return self
    
    def add_custom_validator(self, validator: Callable[[Dict[str, Any]], List[ValidationIssue]]) -> 'ValidationSchema':
        """Додати кастомний валідатор"""
        self.custom_validators.append(validator)
        return self
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Валідувати дані згідно схеми"""
        issues = []
        
        # Валідація правил
        for rule in self.rules:
            issue = rule.validate(data)
            if issue:
                issues.append(issue)
        
        # Кастомні валідатори
        for validator in self.custom_validators:
            custom_issues = validator(data)
            issues.extend(custom_issues)
        
        return ValidationResult(is_valid=len(issues) == 0, issues=issues)


class ValidationSystem:
    """Система валідації"""
    
    def __init__(self):
        self.schemas: Dict[str, ValidationSchema] = {}
        self.validators: Dict[str, Callable[[Any], bool]] = {}
        
        # Ініціалізувати базові валідатори
        self._initialize_validators()
    
    def register_schema(self, schema: ValidationSchema) -> None:
        """Зареєструвати схему валідації"""
        self.schemas[schema.name] = schema
        LOG.info(f"Зареєстровано схему валідації: {schema.name}")
    
    def register_validator(self, name: str, validator: Callable[[Any], bool]) -> None:
        """Зареєструвати валідатор"""
        self.validators[name] = validator
        LOG.info(f"Зареєстровано валідатор: {name}")
    
    def validate(self, data: Dict[str, Any], schema_name: str) -> ValidationResult:
        """Валідувати дані згідно схеми"""
        if schema_name not in self.schemas:
            raise ValueError(f"Схема валідації не знайдена: {schema_name}")
        
        schema = self.schemas[schema_name]
        return schema.validate(data)
    
    def validate_file(self, file_path: Union[str, Path], schema_name: str) -> ValidationResult:
        """Валідувати файл конфігурації"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return ValidationResult(
                is_valid=False,
                issues=[ValidationIssue(
                    field_path="file",
                    message=f"Файл не існує: {file_path}",
                    level=ValidationLevel.ERROR,
                    severity=ValidationSeverity.CRITICAL
                )]
            )
        
        try:
            # Завантажити файл
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() in {'.yaml', '.yml'}:
                    data = yaml.safe_load(f)
                elif file_path.suffix.lower() == '.json':
                    data = json.load(f)
                else:
                    return ValidationResult(
                        is_valid=False,
                        issues=[ValidationIssue(
                            field_path="file",
                            message=f"Непідтримуваний формат файлу: {file_path.suffix}",
                            level=ValidationLevel.ERROR,
                            severity=ValidationSeverity.CRITICAL
                        )]
                    )
            
            # Валідувати дані
            return self.validate(data, schema_name)
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                issues=[ValidationIssue(
                    field_path="file",
                    message=f"Помилка завантаження файлу: {e}",
                    level=ValidationLevel.ERROR,
                    severity=ValidationSeverity.CRITICAL
                )]
            )
    
    def generate_report(self, result: ValidationResult, 
                       include_suggestions: bool = True) -> str:
        """Згенерувати звіт валідації"""
        report = []
        report.append("=" * 60)
        report.append("ЗВІТ ВАЛІДАЦІЇ")
        report.append("=" * 60)
        
        # Загальний статус
        status = "✅ ВАЛІДНА" if result.is_valid else "❌ НЕВАЛІДНА"
        report.append(f"Статус: {status}")
        report.append(f"Всього проблем: {result.summary['total_issues']}")
        report.append(f"Помилок: {result.summary['errors']}")
        report.append(f"Попереджень: {result.summary['warnings']}")
        report.append("")
        
        # Деталі по серйозності
        if result.summary['critical'] > 0:
            report.append(f"🔴 Критичні: {result.summary['critical']}")
        if result.summary['high'] > 0:
            report.append(f"🟠 Серйозні: {result.summary['high']}")
        if result.summary['medium'] > 0:
            report.append(f"🟡 Середні: {result.summary['medium']}")
        if result.summary['low'] > 0:
            report.append(f"🔵 Низькі: {result.summary['low']}")
        report.append("")
        
        # Детальний список проблем
        if result.issues:
            report.append("ДЕТАЛІ ПРОБЛЕМ:")
            report.append("-" * 40)
            
            for i, issue in enumerate(result.issues, 1):
                # Іконка за серйозністю
                icon = "🔴" if issue.severity == ValidationSeverity.CRITICAL else \
                       "🟠" if issue.severity == ValidationSeverity.HIGH else \
                       "🟡" if issue.severity == ValidationSeverity.MEDIUM else "🔵"
                
                report.append(f"{i}. {icon} {issue.field_path}")
                report.append(f"   {issue.message}")
                
                if issue.expected_value and issue.actual_value:
                    report.append(f"   Очікувалось: {issue.expected_value}")
                    report.append(f"   Отримано: {issue.actual_value}")
                
                if include_suggestions and issue.suggestion:
                    report.append(f"   💡 Рекомендація: {issue.suggestion}")
                
                report.append("")
        
        return "\n".join(report)
    
    def _initialize_validators(self) -> None:
        """Ініціалізувати базові валідатори"""
        # Валідатор для email
        self.register_validator("email", lambda x: isinstance(x, str) and "@" in x and "." in x)
        
        # Валідатор для URL
        self.register_validator("url", lambda x: isinstance(x, str) and x.startswith(("http://", "https://")))
        
        # Валідатор для позитивного числа
        self.register_validator("positive_number", lambda x: isinstance(x, (int, float)) and x > 0)
        
        # Валідатор для кольору RGB
        self.register_validator("rgb_color", lambda x: isinstance(x, list) and len(x) == 3 and 
                               all(isinstance(c, (int, float)) and 0 <= c <= 1 for c in x))


# Приклад використання
if __name__ == "__main__":
    # Налаштування логування
    logging.basicConfig(level=logging.INFO)
    
    # Створення системи валідації
    validation_system = ValidationSystem()
    
    # Створення схеми валідації для pack конфігурації
    pack_schema = ValidationSchema("pack_config", "1.0")
    
    # Додати правила валідації
    pack_schema.add_rule(ValidationRule(
        field_path="seed",
        validator=lambda x: isinstance(x, int) and x >= 0,
        message="Seed повинен бути невід'ємним цілим числом",
        required=True,
        data_type=int
    ))
    
    pack_schema.add_rule(ValidationRule(
        field_path="image_size",
        validator=lambda x: isinstance(x, list) and len(x) == 2 and all(isinstance(i, int) for i in x),
        message="image_size повинен бути списком з двох цілих чисел",
        required=True,
        data_type=list
    ))
    
    pack_schema.add_rule(ValidationRule(
        field_path="shots",
        validator=lambda x: isinstance(x, list) and len(x) > 0,
        message="shots повинен бути непустим списком",
        required=True,
        data_type=list
    ))
    
    # Зареєструвати схему
    validation_system.register_schema(pack_schema)
    
    # Приклад валідації
    test_data = {
        "seed": 1337,
        "image_size": [1280, 720],
        "shots": [
            {
                "id": "shot_1001",
                "palette": [[0.1, 0.2, 0.3]],
                "portal": {"center": [0.5, 0.5], "radius": 0.2}
            }
        ]
    }
    
    # Валідувати дані
    result = validation_system.validate(test_data, "pack_config")
    
    # Згенерувати звіт
    report = validation_system.generate_report(result)
    print(report)