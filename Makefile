PYTHON=python
run:
	uvicorn app.main:app --reload

runold:
	python -m uvicorn copyIA:app --reload --host 0.0.0.0 --port 8000
