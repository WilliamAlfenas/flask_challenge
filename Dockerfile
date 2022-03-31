FROM tiangolo/uwsgi-nginx-flask:python3.7

# Setup all python related enviroment
ENV PYTHONUNBUFFERED 1
# RUN apt-get -y update
#RUN apt-get install -y python3 python3-pip python3-dev python-dev postgresql-client libpq-dev python-psycopg2

# Set the working directory
# RUN mkdir /app
WORKDIR /app

# Copy the current directory contents into the container
ADD . /app/

# Install any needed packages specified in requirements.txt
RUN pip3 install -r requirements.txt
RUN apt-get -y update && apt-get -y autoremove

CMD ["./start.sh"]
