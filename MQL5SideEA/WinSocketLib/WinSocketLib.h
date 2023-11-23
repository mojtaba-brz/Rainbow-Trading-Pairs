#ifndef __WIN_SOCKT_LIB_H__
#define __WIN_SOCKT_LIB_H__

#include <windows.h>

/*  To use this exported function of dll, include this header
 *  in your project.
 */

#ifdef BUILD_DLL
    #define DLL_EXPORT __declspec(dllexport)
#else
    #define DLL_EXPORT __declspec(dllimport)
#endif


#ifdef __cplusplus
extern "C"
{
#endif

void DLL_EXPORT HelloWorldDll(void);
long long unsigned int DLL_EXPORT WinSocketCreate();
bool DLL_EXPORT WinSocketConnect(int socket_index, char *host, int port);
bool DLL_EXPORT WinSocketClose(int socket_index);
bool DLL_EXPORT WinSocketConnected(int socket_index);
int DLL_EXPORT WinSocketRead(int socket_index, char *buf, int len);
int DLL_EXPORT WinSocketSend(int socket_index, char *buf, int len);

#ifdef __cplusplus
}
#endif

#endif
