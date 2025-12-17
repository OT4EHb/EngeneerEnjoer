#!/bin/bash
# run_tests.sh

echo "Запуск модульных тестов..."
pytest tests/test_models/ tests/test_schemas/  -v
