#include "WinSocketLib.h"

// a sample exported function
void DLL_EXPORT HelloWorldDll(void)
{
    MessageBoxA(0, "Hello World Form Dll !!!", "DLL Message", MB_OK | MB_ICONINFORMATION);
}

long long unsigned int DLL_EXPORT WinSocketCreate()
{
    return socket(AF_INET, SOCK_STREAM, 0);
}

bool DLL_EXPORT WinSocketConnect(int socket_index, char *host, int port)
{
    // The sockaddr_in structure specifies the address family,
    // IP address, and port of the server to be connected to.
    sockaddr_in clientService;
    clientService.sin_family = AF_INET;
    clientService.sin_addr.s_addr = inet_addr(host);
    clientService.sin_port = htons(port);
    //----------------------
    // Connect to server.
    return (connect(socket_index, (SOCKADDR *) & clientService, sizeof (clientService)) == 0);
}

bool DLL_EXPORT WinSocketClose(int socket_index)
{
    return (closesocket(socket_index) == 0);
}

bool DLL_EXPORT WinSocketConnected(int socket_index)
{
    int nRet;
    fd_set fdread;

    if(( nRet = select( 0, &fdread, NULL, NULL, NULL )) == SOCKET_ERROR )
    {
        // Error condition
        // Check WSAGetLastError
        return false;
    }

    if( nRet > 0 )
    {
        // select() will return value 1 because i m using only one socket
        // At this point, it should be checked whether the
        // socket is part of a set.
        return true;
    }

    return false;
}

int DLL_EXPORT WinSocketRead(int socket_index, char *buf, int len)
{
    return recv(socket_index, buf, len, 0);
}

int DLL_EXPORT WinSocketSend(int socket_index, char *buf, int len)
{
    return send(socket_index, buf, len, 0);
}

extern "C" DLL_EXPORT BOOL APIENTRY DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved)
{
    switch (fdwReason)
    {
        case DLL_PROCESS_ATTACH:
            // attach to process
            // return FALSE to fail DLL load
            break;

        case DLL_PROCESS_DETACH:
            // detach from process
            break;

        case DLL_THREAD_ATTACH:
            // attach to thread
            break;

        case DLL_THREAD_DETACH:
            // detach from thread
            break;
    }
    return TRUE; // succesful
}
