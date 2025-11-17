

import re
import sys
import os
from typing import List, Tuple

class SQLSecurityScanner:
    def __init__(self):
        self.vulnerabilities = []
        self.patterns = {
            'sql_injection': [
                # Паттерны для конкатенации строк
                r"(\+\s*['\"])",
                r"(CONCAT\s*\()",
                # Динамический SQL
                r"(EXEC\s*\(\s*@)",
                r"(EXECUTE\s*\(\s*@)",
                r"(sp_executesql)",
                # Потенциально опасные функции
                r"(xp_cmdshell)",
                r"(xp_)",
                # Прямое использование пользовательского ввода
                r"(\$\{[^}]+\})",
                r"(\{\{[^}]+\}\})"
            ],
            'hardcoded_credentials': [
                r"(password\s*=\s*['\"][^'\"]+['\"])",
                r"(pwd\s*=\s*['\"][^'\"]+['\"])",
                r"(PASSWORD\s*=\s*['\"][^'\"]+['\"])"
            ],
            'weak_authentication': [
                r"(IDENTIFIED BY\s+['\"][^'\"]{1,5}['\"])",  # Короткие пароли
                r"(PASSWORD\s*\(\s*['\"][^'\"]{1,5}['\"]\s*\))"
            ],
            'information_disclosure': [
                r"(SELECT\s+\*\s+FROM)",  # SELECT * без ограничений
                r"(INSERT\s+INTO\s+\w+\s+VALUES)",  # INSERT без указания колонок
                r"(dbo\.sys)",
                r"(INFORMATION_SCHEMA\..*WHERE\s+1=1)"
            ]
        }
    
    def scan_file(self, filename: str) -> List[Tuple[str, str, int]]:
        """Сканирует SQL файл на уязвимости"""
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Файл {filename} не найден")
        
        if not filename.lower().endswith('.sql'):
            raise ValueError(f"Файл {filename} не является SQL файлом")
        
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
        
        return self.scan_content(content, filename)
    
    def scan_content(self, content: str, filename: str) -> List[Tuple[str, str, int]]:
        """Сканирует содержимое SQL на уязвимости"""
        vulnerabilities = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_clean = line.strip().upper()
            
            # Пропускаем комментарии и пустые строки
            if line_clean.startswith('--') or line_clean.startswith('/*') or not line_clean:
                continue
            
            # Проверяем каждую категорию уязвимостей
            for category, patterns in self.patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        vulnerabilities.append((
                            category,
                            line.strip(),
                            line_num
                        ))
        
        # Дополнительные проверки
        vulnerabilities.extend(self._check_additional_vulnerabilities(content, lines))
        
        return vulnerabilities
    
    def _check_additional_vulnerabilities(self, content: str, lines: List[str]) -> List[Tuple[str, str, int]]:
        """Дополнительные проверки безопасности"""
        vulnerabilities = []
        
        # Проверка на отсутствие WHERE в DELETE/UPDATE
        for line_num, line in enumerate(lines, 1):
            line_clean = line.strip().upper()
            
            # DELETE без WHERE
            if re.match(r'^DELETE\s+FROM\s+\w+\s*$', line_clean) or \
               re.match(r'^DELETE\s+FROM\s+\w+\s*;', line_clean):
                vulnerabilities.append((
                    'unsafe_delete',
                    line.strip(),
                    line_num
                ))
            
            # UPDATE без WHERE
            if re.match(r'^UPDATE\s+\w+\s+SET\s+[^;]+\s*$', line_clean) and \
               'WHERE' not in line_clean:
                vulnerabilities.append((
                    'unsafe_update',
                    line.strip(),
                    line_num
                ))
        
        return vulnerabilities
    
    def print_report(self, vulnerabilities: List[Tuple[str, str, int]], filename: str):
        """Выводит отчет о найденных уязвимостях"""
        if not vulnerabilities:
            print(f"✓ Файл {filename} прошел проверку безопасности. Уязвимостей не найдено.")
            return
        
        print(f"⚠️  Найдены потенциальные уязвимости в файле {filename}:")
        print("=" * 80)
        
        for i, (category, code, line_num) in enumerate(vulnerabilities, 1):
            category_name = self._get_category_name(category)
            print(f"{i}. Тип: {category_name}")
            print(f"   Строка {line_num}: {code}")
            print(f"   Рекомендация: {self._get_recommendation(category)}")
            print("-" * 80)
    
    def _get_category_name(self, category: str) -> str:
        """Возвращает читаемое название категории уязвимости"""
        names = {
            'sql_injection': 'SQL инъекция',
            'hardcoded_credentials': 'Жестко заданные учетные данные',
            'weak_authentication': 'Слабая аутентификация',
            'information_disclosure': 'Раскрытие информации',
            'unsafe_delete': 'Небезопасный DELETE',
            'unsafe_update': 'Небезопасный UPDATE'
        }
        return names.get(category, category)
    
    def _get_recommendation(self, category: str) -> str:
        """Возвращает рекомендацию по исправлению уязвимости"""
        recommendations = {
            'sql_injection': 'Используйте параметризованные запросы и хранимые процедуры',
            'hardcoded_credentials': 'Не храните пароли в коде, используйте защищенные хранилища',
            'weak_authentication': 'Используйте сложные пароли длиной не менее 8 символов',
            'information_disclosure': 'Ограничивайте выборку данных и не используйте SELECT *',
            'unsafe_delete': 'Всегда используйте WHERE в операторах DELETE',
            'unsafe_update': 'Всегда используйте WHERE в операторах UPDATE'
        }
        return recommendations.get(category, 'Проверьте безопасность кода')

def main():
    if len(sys.argv) != 2:
        print("Использование: python sql_scanner.py <filename.sql>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        scanner = SQLSecurityScanner()
        vulnerabilities = scanner.scan_file(filename)
        scanner.print_report(vulnerabilities, filename)
        
        # Возвращаем код ошибки 1 если найдены уязвимости
        if vulnerabilities:
            print(f"\n❌ Найдено {len(vulnerabilities)} уязвимостей. Код возврата: 1")
            sys.exit(1)
        else:
            print(f"\n✅ Проверка завершена успешно. Код возврата: 0")
            sys.exit(0)
            
    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()