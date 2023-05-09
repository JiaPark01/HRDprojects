#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <stdbool.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <pthread.h>

#define MAX_CLIENT 256
int client_count = 0;
int client_sockets[MAX_CLIENT] = {0, };
pthread_mutex_t mutex_key = PTHREAD_MUTEX_INITIALIZER;

void error_handling(const char*);
void sending_message(const char*, int);
void* handling_client(void*);   // task func called by thread

char turn[1];

int main(int argc, const char* argv[])
{
    int serv_sock = 0;
    int clnt_sock = 0;
    struct sockaddr_in serv_addr;
    struct sockaddr_in clnt_addr;

    memset(&serv_addr, 0, sizeof serv_addr);
    memset(&clnt_addr, 0, sizeof clnt_addr);
    
    int clnt_addr_size = 0;
    
    pthread_t pthread_id = 0ul;

    if (argc != 2) error_handling("./TICTACTOE_SERVER 9999");
    
    pthread_mutex_init(&mutex_key, NULL);

    // 1. socket()
    if ((serv_sock = socket(PF_INET, SOCK_STREAM, 0)) == -1) error_handling("socket() error");
    
    // 1.5 serv_addr init
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    serv_addr.sin_port = htons(atoi(argv[1]));
    
    // 2. bind()
    if (bind(serv_sock, (const struct sockaddr*)&serv_addr, sizeof serv_addr) == -1) error_handling("bind() error");
    
    // 3. listen()
    if (listen(serv_sock, 5) == -1) error_handling("listen() error");

    // 4. accept()
    while(true) {
        clnt_addr_size = sizeof clnt_addr;
        if ((clnt_sock = accept(serv_sock, (struct sockaddr*)&clnt_addr, (socklen_t*)&clnt_addr_size)) == -1) error_handling("accept() error");

        pthread_mutex_lock(&mutex_key);
        client_sockets[client_count++] = clnt_sock;
        pthread_mutex_unlock(&mutex_key);

        pthread_create(&pthread_id, NULL, handling_client, (void*)&clnt_sock);
        pthread_detach(pthread_id); // if use join, it gets blocked and cannot go through the loop

        fprintf(stdout, "Connected client IP : %s\r\n", inet_ntoa(clnt_addr.sin_addr));
    }
    
    close(serv_sock);

    return 0;
}

void error_handling(const char* _msg)
{
    fputs(_msg, stderr);
    fputs("\r\n", stderr);

    exit(1);

    return;
}

void sending_message(const char* _msg, int _str_len)
{
    pthread_mutex_lock(&mutex_key);
    for (int i = 0; i < client_count; ++i) {
        //sprintf(turn, "%d ", i);
        //write(client_sockets[i], turn, sizeof client_count);
        write(client_sockets[i], _msg, _str_len);
    }
    pthread_mutex_unlock(&mutex_key);
    
    return;
}

void* handling_client(void* args)
{
    int client_sock = *((int*)args);
    int str_len = 0;
    char message[BUFSIZ] = {'\0', };
    
    sprintf(message, "%d ", turn);
    sending_message(message, 10);
    while((str_len = read(client_sock, message, BUFSIZ - 1)) != 0) {
        sending_message(message, str_len);
    }
       
    // garbage collecting
    for (int i = 0; i < client_count; ++i) {
        pthread_mutex_lock(&mutex_key);
        if (client_sock == client_sockets[i]) {
            while(i++ < client_count - 1) {
                client_sockets[i] = client_sockets[i + 1];
            }
            break;
        }
    }
    --client_count;
    fputs("Client disconnected...\r\n", stdout);
    pthread_mutex_unlock(&mutex_key);
    close(client_sock);

    return NULL;
}
