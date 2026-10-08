#include <windows.h>
#include <tlhelp32.h>
#include <tchar.h>
#include <string>
#include <stdio.h>

#include <UIAutomation.h>
#pragma comment(lib, "uiautomationcore.lib")

HWND g_HWND = NULL;

/////////////////////////////////////////////////////HWND////////////////////////////////////////////////////////////////
BOOL CALLBACK EnumWindowsProcMy(HWND hwnd, LPARAM lParam)
{
    DWORD lpdwProcessId;
    GetWindowThreadProcessId(hwnd, &lpdwProcessId);
    if (lpdwProcessId == lParam)
    {
        g_HWND = hwnd;
        return FALSE;
    }
    return TRUE;
}

DWORD retrieveProcessHandle(const wchar_t* name)
{ // stores handle in gHandler
    PROCESSENTRY32 entry;
    entry.dwSize = sizeof(PROCESSENTRY32);
    bool running = 0;

    HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    DWORD pId = 0;

    if (Process32First(snapshot, &entry))
    {
        do
        {
            if (_tcsicmp(entry.szExeFile, name) == 0)
            {
                printf("HW is running already! ProcessHandle can be retrieved. \n");
                running = 1;
                HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, entry.th32ProcessID);
                pId = GetProcessId(hProcess);

                /*
                SDL_SetWindowAlwaysOnTop(mWindow, SDL_TRUE);
                gHandlerp->HWAlive = 1;
                CreateSampleSelectScreen();
                screenType = SampleSelectScreen;
                CloseHandle(snapshot);
                return;
                */
                // don't work no more
                CloseHandle(snapshot);
            }
        } while (Process32Next(snapshot, &entry));
    }
    //CloseHandle(snapshot);
    return pId;
}

/////////////////////////////////////////////////////CTRL M Shortcut////////////////////////////////////////////////////////////////
void SendCtrlM(HWND hwnd)
{
    // Press Ctrl
    PostMessage(hwnd, WM_KEYDOWN, VK_CONTROL, 0);

    // Press M
    PostMessage(hwnd, WM_KEYDOWN, 'M', 0);

    // Release M
    PostMessage(hwnd, WM_KEYUP, 'M', 0);

    // Release Ctrl
    PostMessage(hwnd, WM_KEYUP, VK_CONTROL, 0);
}

void SendCtrlPlus(HWND hwnd, char letter)
{
    // Bring target window to foreground
    SetForegroundWindow(hwnd);

    INPUT inputs[4] = {};

    // CTRL down
    inputs[0].type = INPUT_KEYBOARD;
    inputs[0].ki.wVk = VK_CONTROL;

    // M down
    inputs[1].type = INPUT_KEYBOARD;
    inputs[1].ki.wVk = letter;

    // M up
    inputs[2].type = INPUT_KEYBOARD;
    inputs[2].ki.wVk = letter;
    inputs[2].ki.dwFlags = KEYEVENTF_KEYUP;

    // CTRL up
    inputs[3].type = INPUT_KEYBOARD;
    inputs[3].ki.wVk = VK_CONTROL;
    inputs[3].ki.dwFlags = KEYEVENTF_KEYUP;

    SendInput(4, inputs, sizeof(INPUT));
}


/////////////////////////////////////////////////////Clicking Buttons Class///////////////////////////////////////////////////////
class UIAHelper
{
public:
    UIAHelper() : automation(nullptr), root(nullptr)
    {
        CoInitialize(NULL);

        CoCreateInstance(
            CLSID_CUIAutomation,
            NULL,
            CLSCTX_INPROC_SERVER,
            IID_IUIAutomation,
            (void**)&automation
        );
    }

    ~UIAHelper()
    {
        if (root) root->Release();
        if (automation) automation->Release();
        CoUninitialize();
    }

    // Attach to window by title
    bool AttachToWindow(const std::wstring& windowTitle)
    {
        HWND hwnd = FindWindow(NULL, windowTitle.c_str());
        if (!hwnd) return false;

        if (root) { root->Release(); root = nullptr; }

        return SUCCEEDED(automation->ElementFromHandle(hwnd, &root));
    }

    //attach by HWND
    bool AttachToWindow(HWND hwnd)
    {
        if (!hwnd) return false;

        if (root) { root->Release(); root = nullptr; }

        return SUCCEEDED(automation->ElementFromHandle(hwnd, &root));
    }

    // Click button by name
    bool ClickButton(const std::wstring& name)
    {
        if (!automation || !root) {
            printf("No root or automation\n");
            return false;
        }

        SetForegroundWindow(g_HWND);  // important

        IUIAutomationCondition* condition = nullptr;
        VARIANT var;
        var.vt = VT_BSTR;
        var.bstrVal = SysAllocString(name.c_str());

        HRESULT hr = automation->CreatePropertyCondition(UIA_NamePropertyId, var, &condition);

        SysFreeString(var.bstrVal);
        if (FAILED(hr) || !condition) {
            printf("Couldn't find button name\n");
            return false;
        }

        IUIAutomationElement* element = nullptr;
        hr = root->FindFirst(TreeScope_Subtree, condition, &element);

        condition->Release();

        if (FAILED(hr) || !element) {
            printf("Couldn't find button something\n");
            return false;
        }

        bool success = Invoke(element);

        element->Release();
        return success;
    }
    bool OpenFileByName(const std::wstring& filename);
    bool WaitAndOpenFile(const std::wstring& fileName, int timeoutMs = 5000);

private:
    IUIAutomation* automation;
    IUIAutomationElement* root;

    bool Invoke(IUIAutomationElement* element)
    {
        IUIAutomationInvokePattern* invoke = nullptr;

        HRESULT hr = element->GetCurrentPatternAs(
            UIA_InvokePatternId,
            IID_IUIAutomationInvokePattern,
            (void**)&invoke
        );

        if (FAILED(hr) || !invoke)
            return false;

        hr = invoke->Invoke();

        invoke->Release();
        return SUCCEEDED(hr);
    }
};



/////////////////////////////////////////////////////Opening files////////////////////////////////////////////////////////////////
bool UIAHelper::OpenFileByName(const std::wstring& filename)
{
    IUIAutomationCondition* condition = nullptr;

    VARIANT var;
    var.vt = VT_BSTR;
    var.bstrVal = SysAllocString(filename.c_str());

    automation->CreatePropertyCondition(
        UIA_NamePropertyId,
        var,
        &condition
    );

    SysFreeString(var.bstrVal);

    automation->GetRootElement(&root);  // switch to desktop root

    if (!root) {
        return false;
    }

    IUIAutomationElement* item = nullptr;
    root->FindFirst(TreeScope_Subtree, condition, &item);

    condition->Release();

    if (!item) return false;

    IUIAutomationInvokePattern* invoke = nullptr;

    HRESULT hr = item->GetCurrentPatternAs(
        UIA_InvokePatternId,
        IID_IUIAutomationInvokePattern,
        (void**)&invoke
    );

    if (SUCCEEDED(hr) && invoke)
    {
        invoke->Invoke();  // acts like double-click

        invoke->Release();
        item->Release();
        return true;
    }

    item->Release();
    return false;
}

bool UIAHelper::WaitAndOpenFile(const std::wstring& fileName, int timeoutMs)
{
    automation->GetRootElement(&root);  // switch to desktop root

    if (!root) {
        return false;
    }

    // Create condition: Name == fileName
    VARIANT var;
    var.vt = VT_BSTR;
    var.bstrVal = SysAllocString(fileName.c_str());

    IUIAutomationCondition* cond = nullptr;
    automation->CreatePropertyCondition(UIA_NamePropertyId, var, &cond);

    SysFreeString(var.bstrVal);

    if (!cond)
    {
        root->Release();
        return false;
    }

    IUIAutomationElement* item = nullptr;

    const int sleepStep = 100;
    int waited = 0;

    // Wait loop for dialog/file to appear
    while (waited < timeoutMs)
    {
        HRESULT hr = root->FindFirst(TreeScope_Subtree, cond, &item);

        if (SUCCEEDED(hr) && item)
            break;  // Found it

        Sleep(sleepStep);
        waited += sleepStep;
    }

    cond->Release();

    if (!item)
    {
        root->Release();
        return false; // not found in time
    }

    // Invoke (double-click equivalent)
    IUIAutomationInvokePattern* invoke = nullptr;

    HRESULT hr = item->GetCurrentPatternAs(
        UIA_InvokePatternId,
        IID_IUIAutomationInvokePattern,
        (void**)&invoke
    );

    if (SUCCEEDED(hr) && invoke)
    {
        invoke->Invoke();  // OPEN FILE

        invoke->Release();
        item->Release();
        root->Release();
        return true;
    }

    item->Release();
    root->Release();
    return false;
}


int main() {

    DWORD pId = retrieveProcessHandle(L"Hauptwerk.exe");
    if (pId != 0) {
        EnumWindows(EnumWindowsProcMy, pId); //retrieve HWND
    }
    else {
        printf("Hauptwerk.exe could not be found");
        return 1;
    }

    //SendCtrlPlus(g_HWND, 'M'); //HW9
    SendCtrlPlus(g_HWND, 'L'); //HW7

    UIAHelper uia;
    uia.AttachToWindow(g_HWND); // change your helper to accept HWND

    //click load
    //uia.ClickButton(L"Load MIDI file ...");

    std::wstring fileName = L"Hauptwerk recording, 2026-04-15-12-00-20 (Smecno Surr Ext).mid";
    uia.WaitAndOpenFile(fileName);
    
    Sleep(5000);

    SendCtrlPlus(g_HWND, 'L'); //HW7
    fileName = L"Hauptwerk recording, 2026-04-23-14-01-07 (Smecno Surr Ext).mid";
    uia.WaitAndOpenFile(fileName);
    //uia.WaitAndOpenFile(automation, fileName);

    return 0;
}