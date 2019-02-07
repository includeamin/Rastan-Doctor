FROM node:8
EXPOSE 3030

WORKDIR /usr/src/app/serviceManage

COPY  package*.json ./
COPY package.json ./

COPY . .
RUN npm install
RUN npm install express
RUN npm install mongodb
RUN npm install body-parser
RUN npm install node-fetch

CMD ["node","index.js"]

