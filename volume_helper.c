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


int main(){
    return 0;
}