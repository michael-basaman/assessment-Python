.PHONY: run tidy

run:
	uvicorn app.main:app --host 0.0.0.0 --port $${PORT:-4001}

tidy:
	pip install -r requirements.txt
