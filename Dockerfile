FROM ubuntu:20.04
RUN apt update
RUN apt install -y python3 python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install flask pymongo
RUN mkdir -p /DSPharmacy
WORKDIR /DSPharmacy
ADD . .
EXPOSE 5000
ENTRYPOINT [ "python3", "-u", "app.py" ]