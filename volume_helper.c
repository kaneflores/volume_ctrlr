#include <stdio.h>
//
/*
    volume_helper.c
    Windows per_application volume controller using Core audio (WASAPI).
    Compile with MinGW:
        gcc volume


*/

#define COBJMACROS
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <mmdeviceapi.h>
#include <audiopolicy.h>
#include <endpointvolume.h>
#include <psapi.h>
#include <stdlib.h>
#include <string.h>

DEFINE_GUID(CLSID_MMDeviceEnumerator, 0xBCDE0395,0xE52F,0x467C,0x8E,0x3D,0xC4,0x57,0x92,0x91,0x69,0x2E);
DEFINE_GUID(IID_IMMDeviceEnumerator,  0xA95664D2,0x9614,0x4F35,0xA7,0x46,0xDE,0x8D,0xB6,0x36,0x17,0xE6);
DEFINE_GUID(IID_IAudioSessionManager2,0x77AA99A0,0x1BD6,0x484F,0x8B,0xC7,0x2C,0x65,0x4C,0x9A,0x9B,0x6F);
DEFINE_GUID(IID_ISimpleAudioVolume,   0x87CE5498,0x68D6,0x44E5,0x92,0x15,0x6D,0xA4,0x7E,0xF8,0x83,0xD8);
DEFINE_GUID(IID_IAudioEndpointVolume, 0x5CDF2C82,0x841E,0x4546,0x97,0x22,0xCF,0x7F,0xA0,0x79,0x00,0x92);

static IMMDevice* get_default_device(void){
    IMMDeviceEnumerator *enumerator = NULL;
    IMMDevice *device = NULL;
    HRESULT hr = CoCreateInstance(&CLSID_MMDeviceEnumerator, NULL, CLSCTX_ALL,
                            &IID_IMMDeviceEnumerator, (void**)&enumerator);
    
    if (FAILED(hr)) return NULL;
    hr = IMMDeviceEnumerator_GetDefaultAudioEndpoint(enumerator, eRender, eConsole, &device);
    IMMDeviceEnumerator_Release(enumerator);
    if (FAILED(hr)) return NULL;
    return device;
}

static void get_process_name(DWORD pid, char *buf, int buflen){
    HANDLE hProc = OpenProcess(PROCESS_QUERY_LIMITEDINFORMATION, FALSE, pid);
    if (!hProc){ strncpy(buf, "Unknown", buflen); return;}
    char path[MAX_PATH] = {0};
    DWORD sz = MAX_PATH;
    if (QueryFullProcessImageNameA(hProc, 0, path, &sz)){
        char *slash = strrchr(path, '\\');
        if (slash){strncpy(buf, slash + 1, buflen);}
        else{
            strncpy(buf, path, buflen);
        }
    }else{
        strncpy(buf, "Unknown", buflen);

    }
    
}
int main(){
    return 0;
}