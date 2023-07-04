FROM python:3.10-slim
WORKDIR /code

RUN pip install numpy pandas grpcio streamlit
ADD ./fxapp/fx-dashboard/requirements.txt /code/
RUN pip3 install -r /code/requirements.txt
ADD ./fxapp/fx-dashboard/ /code/

ENTRYPOINT streamlit run app.py