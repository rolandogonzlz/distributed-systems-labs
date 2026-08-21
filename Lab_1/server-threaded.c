#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>
#include <arpa/inet.h>
#include <pthread.h>

#define BUFFER_SIZE 1024


void *handle_client(void *arg)
{
    int clientSocket = *((int *) arg);

    free(arg);

    char buffer[BUFFER_SIZE];

    int bytesReceived = recv(
        clientSocket,
        buffer,
        BUFFER_SIZE - 1,
        0
    );

    if (bytesReceived > 0)
    {
        buffer[bytesReceived] = '\0';

        printf(
            "[THREAD] Received: %s\n",
            buffer
        );

        for (int i = 0; i < bytesReceived; i++)
        {
            buffer[i] = toupper(
                (unsigned char) buffer[i]
            );
        }

        sleep(3);

        send(
            clientSocket,
            buffer,
            bytesReceived,
            0
        );

        printf(
            "[THREAD] Response sent\n"
        );
    }

    close(clientSocket);

    printf(
        "[THREAD] Connection closed\n"
    );

    return NULL;
}


int main(int argc, char *argv[])
{
    int port = 22000;

    if (argc >= 2)
    {
        port = atoi(argv[1]);
    }

    int serverSocket = socket(
        AF_INET,
        SOCK_STREAM,
        0
    );

    if (serverSocket < 0)
    {
        perror("socket");
        return 1;
    }

    int option = 1;

    setsockopt(
        serverSocket,
        SOL_SOCKET,
        SO_REUSEADDR,
        &option,
        sizeof(option)
    );

    struct sockaddr_in serverAddress;

    memset(
        &serverAddress,
        0,
        sizeof(serverAddress)
    );

    serverAddress.sin_family = AF_INET;
    serverAddress.sin_addr.s_addr = INADDR_ANY;
    serverAddress.sin_port = htons(port);

    if (
        bind(
            serverSocket,
            (struct sockaddr *) &serverAddress,
            sizeof(serverAddress)
        ) < 0
    )
    {
        perror("bind");
        close(serverSocket);
        return 1;
    }

    if (listen(serverSocket, 10) < 0)
    {
        perror("listen");
        close(serverSocket);
        return 1;
    }

    printf(
        "C threaded server ready on port %d\n",
        port
    );

    while (1)
    {
        struct sockaddr_in clientAddress;
        socklen_t clientLength =
            sizeof(clientAddress);

        int *clientSocket =
            malloc(sizeof(int));

        *clientSocket = accept(
            serverSocket,
            (struct sockaddr *) &clientAddress,
            &clientLength
        );

        if (*clientSocket < 0)
        {
            perror("accept");
            free(clientSocket);
            continue;
        }

        printf(
            "Client connected: %s:%d\n",
            inet_ntoa(clientAddress.sin_addr),
            ntohs(clientAddress.sin_port)
        );

        pthread_t thread;

        if (
            pthread_create(
                &thread,
                NULL,
                handle_client,
                clientSocket
            ) != 0
        )
        {
            perror("pthread_create");
            close(*clientSocket);
            free(clientSocket);
            continue;
        }

        pthread_detach(thread);
    }

    close(serverSocket);

    return 0;
}