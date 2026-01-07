PYTHON=python
run:
	python -m uvicorn app.main:app --reload --no-access-log

runold:
	python -m uvicorn copyIA:app --reload --host 0.0.0.0 --port 8000
