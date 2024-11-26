# Use an official Python image as the base image
FROM python:3.12-bookworm


# Install tesseract ocr with spanish package
RUN apt update && apt install -y apt-transport-https wget && \
    echo "deb [trusted==yes] https://notesalexp.org/tesseract-ocr5/bookworm/ bookworm main" | tee /etc/apt/sources.list.d/notesalexp.list > /dev/null && \
    wget -O - https://notesalexp.org/debian/alexp_key.asc | apt-key add -  && \
    apt update &&  apt-get install -y --allow-unauthenticated tesseract-ocr tesseract-ocr-spa libegl1 libsm6 libxext6 ffmpeg libfontconfig1 libxrender1 libgl1-mesa-glx  && \
    apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/

# Set the working directory
WORKDIR /usr/share/app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install the required packages
RUN pip install -r requirements.txt

# Copy the rest of the application files
COPY site_app/  .


# Collect static files
#RUN python manage.py collectstatic --no-input
RUN find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
RUN find . -path "*/migrations/*.pyc"  -delete


#For production
CMD ["uwsgi","--ini", "uwsgi.ini"]
