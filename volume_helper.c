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
    CloseHandle(hProc);
    
}

static int cmd_list(void){ //checked
    IMMDevice *device = get_default_device();
    if (!device) { fprintf(stderr, "ERROR:no_device\n"); return 1; }

    IAudioSessionManager2 *mgr = NULL;
    IMMDevice_Activate(device, &IID_IAudioSessionManager2, CLSCTX_ALL, NULL, (void**)&mgr);
    IMMDevice_Release(device);
    if (!mgr){ fprintf(stderr, "ERROR:no_manager\n"); return 1;
    }

    IAudioSessionEnumerator *senum = NULL;
    IAudioSessionManager2_GetSessionEnumerator(mgr, &senum);
    IAudioSessionManager2_Release(mgr);
    if (!senum) { fprintf(stderr, "ERROR:no_enumerator\n"); return 1;}

    int count = 0;
    IAudioSessionEnumerator_GetCount(senum, &count);
    
    for (int i = 0; i < count; i++){
        IAudioSessionControl *ctrl = NULL;
        IAudioSessionEnumerator_GetSession(senum, i, &ctrl);
        if (!ctrl) continue;

        IAudioSessionControl2 *ctrl2 = NULL;
        IAudioSessionControl_QueryInterface(ctrl, &(GUID){0xBFB7FF88, 0x7239, 0x4FC9, {0x8F, 0xA2, 0x07, 0xC9, 0x50, 0xBE, 0x9C, 0x6D}},
                                            (void**)&ctrl2);
        IAudioSessionControl_Release(ctrl);
        if (!ctrl2) continue;

        DWORD pid = 0;
        IAudioSessionControl2_GetProcessId(ctrl2, &pid);
        if (pid ==0){ IAudioSessionControl2_Release(ctrl2); continue;}

        ISimpleAudioVolume *vol = NULL;
        IAudioSessionControl2_QueryInterface(ctrl2, &IID_ISimpleAudioVolume, (void**)&vol);
        IAudioSessionControl2_Release(ctrl2);
        if (!vol) continue;

        float fvol = 0.0f;
        BOOL muted = FALSE;
        ISimpleAudioVolume_GetMasterVolume(vol, &fvol);
        ISimpleAudioVolume_GetMute(vol, &muted);
        ISimpleAudioVolume_Release(vol);

        char name[MAX_PATH] = {0};
        get_process_name(pid, name, MAX_PATH);
        printf("%lu|%s|%d|%d\n", (unsigned long)pid, name, (int)(fvol*100+0.5f), muted?1:0);
    }

    IAudioSessionEnumerator_Release(senum);
    return 0;
}
int main(){
    return 0;
}