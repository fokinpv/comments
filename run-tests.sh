#!/bin/bash
flake8 ./comments && PYTHONPATH=. pytest --cov
