#include <windows.h>
#include <string>
#include <iostream>

#pragma comment(lib, "user32.lib")

HWND g_hwnd = nullptr;
int g_receivedCount = 0;

std::string WideToUtf8(const std::wstring& w)
{
    if (w.empty())
        return {};

    int size = WideCharToMultiByte(
        CP_UTF8,
        0,
        w.c_str(),
        -1,
        nullptr,
        0,
        nullptr,
        nullptr
    );

    std::string result(size - 1, '\0');

    WideCharToMultiByte(
        CP_UTF8,
        0,
        w.c_str(),
        -1,
        &result[0],
        size,
        nullptr,
        nullptr
    );

    return result;
}


LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
    switch (msg)
    {
    case WM_COPYDATA:
    {
        COPYDATASTRUCT* cds = (COPYDATASTRUCT*)lParam;

        switch (cds->dwData)
        {
        case 1: // SUBMIT
        {
            const wchar_t* wtext =
                reinterpret_cast<const wchar_t*>(cds->lpData);

            std::wstring wstr(wtext ? wtext : L"");
            std::string text = WideToUtf8(wstr);

            printf("Submitted: %s\n", text.c_str());
            break;
        }

        case 2: // CANCEL
            printf("Keyboard cancelled by user\n");
            break;
        }

        g_receivedCount++; // move to next state

        return TRUE;
    }

    case WM_DESTROY:
        PostQuitMessage(0);
        return 0;
    }

    return DefWindowProc(hwnd, msg, wParam, lParam);
}

void LaunchKeyboard(HWND hwnd)
{
    wchar_t cmdLine[256];
    swprintf(cmdLine, 256, L"%llu", (unsigned long long)hwnd);

    ShellExecute(
        NULL,
        L"open",
        L"keyboard.exe", // make sure it's in working dir
        cmdLine,
        NULL,
        SW_SHOWNORMAL
    );
}


int main()
{
    // --- Create a simple window ---
    WNDCLASS wc = {};
    wc.lpfnWndProc = WndProc;
    wc.lpszClassName = L"MyWindowClass";

    RegisterClass(&wc);

    g_hwnd = CreateWindowEx(
        0,
        wc.lpszClassName,
        L"MyAppWindow",
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT, 400, 300,
        NULL,
        NULL,
        NULL,
        NULL
    );

    ShowWindow(g_hwnd, SW_SHOW);

    // --- First keyboard launch ---
    LaunchKeyboard(g_hwnd);

    MSG msg;

    while (true)
    {
        while (PeekMessage(&msg, NULL, 0, 0, PM_REMOVE))
        {
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }

        if (g_receivedCount == 1)
        {
            std::cout << "Waiting 3 seconds...\n";
            Sleep(3000);

            LaunchKeyboard(g_hwnd);
            g_receivedCount++; // move to next state
        }
        else if (g_receivedCount == 3)
        {
            std::cout << "Done. Exiting.\n";
            break;
        }

        Sleep(10);
    }

    return 0;
}
