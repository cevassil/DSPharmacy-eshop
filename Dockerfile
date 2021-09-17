FROM ubuntu:20.04
RUN apt-get update
RUN apt install -y python3 python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install flask pymongo
RUN mkdir /DSPharmacy
RUN mkdir -p /DSPharmacy/data
RUN mkdir -p /DSPharmacy/templates
ADD templates /DSPharmacy/templates
COPY app.py /DSPharmacy/app.py
ADD data /DSPharmacy/data
EXPOSE 5000
WORKDIR /DSPharmacy
ENTRYPOINT ["python3", "-u", "app.py"]
