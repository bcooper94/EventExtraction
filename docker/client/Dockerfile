FROM node:latest

RUN npm install -g create-react-app
RUN mkdir /client
COPY ./cfp-app /client
WORKDIR /client
RUN ls -al
RUN npm install
RUN ls -al
ENTRYPOINT npm start
#ENTRYPOINT sleep infinity