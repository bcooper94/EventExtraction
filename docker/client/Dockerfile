FROM node:latest

RUN npm install -g create-react-app
RUN mkdir /client
COPY ./cfp-app /client
WORKDIR /client
RUN npm install
ENTRYPOINT npm start
