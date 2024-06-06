FROM gradle:8.6.0-jdk17-jammy AS build
COPY --chown=gradle:gradle . /home/gradle/src
WORKDIR /home/gradle/src
RUN ./gradlew build --no-daemon
RUN ./gradlew test --no-daemon