#Requires AutoHotkey v2.0
#SingleInstance Force

global targetHwnd := 0
global currentText := ""
global scale := 1.0

if (A_Args.Length > 0)
    targetHwnd := Integer(A_Args[1])
	; MsgBox "HWND=" targetHwnd

if (A_Args.Length > 1)
    currentText := A_Args[2]
	
if (A_Args.Length > 2)
	scale := Number(A_Args[3])

S(v) => Round(v * scale)

shift := false
maxLen := 30

mygui := Gui("+AlwaysOnTop +ToolWindow", "Keyboard")
mygui.BackColor := "303030"
mygui.SetFont("s" S(15))

display := mygui.AddEdit(
    "x" S(20) " y" S(10)
    " w" S(650) " h" S(40)
    " ReadOnly",
    currentText
)

btnClear := mygui.AddButton(
    "x" S(680) " y" S(10)
    " w" S(110) " h" S(40),
    "Clear"
)

btnClear.OnEvent("Click", ClearText)

btnW := S(60)
btnH := S(60)
gap  := S(6)

startX := S(20)
startY := S(60)

buttons := []

rows := [
    "1234567890",
    "QWERTYUIOP",
    "ASDFGHJKL",
    "ZXCVBNM.-"
]

y := startY

for rowIndex, rowText in rows
{
    offset := 0
    if (rowIndex = 2)
        offset := S(30)
    else if (rowIndex = 3)
        offset := S(60)
    else if (rowIndex = 4)
        offset := 0

    x := startX + offset

    ; --- Shift (bottom row) ---
    if (rowIndex = 4)
    {
        shiftW := S(100)

		btnShift := mygui.AddButton(
			"x" x " y" y " w" shiftW " h" btnH,
			"Shift"
		)
		x += shiftW + gap
    }

    for char in StrSplit(rowText)
    {
        btn := mygui.AddButton(
            "x" x " y" y " w" btnW " h" btnH,
            StrLower(char)
        )

        btn.Orig := char
        btn.OnEvent("Click", OnCharClick)
        buttons.Push(btn)

        x += btnW + gap
    }

    ; --- Backspace placement (after numbers row) ---
    if (rowIndex = 1)
    {	
		mygui.SetFont("s" S(18))
        btnBack := mygui.AddButton(
            "x" x " y" y " w" S(110) " h" btnH,
            "←"
        )
		mygui.SetFont("s" S(15))
        btnBack.OnEvent("Click", Backspace)
    }

    ; --- Enter (right side) ---
    if (rowIndex = 2)
    {
        enterX := x

		btnEnter := mygui.AddButton(
			"x" enterX
			" y" y
			" w" S(80)
			" h" (btnH*2 + gap),
			"Enter"
		)
        btnEnter.OnEvent("Click", (*) => SubmitText())
    }

    y += btnH + gap
}

; --- Space bar (Bottom) ---
spaceY := y
mygui.AddButton(
    "x" S(200)
	" y" spaceY
	" w" S(420)
	" h" btnH,
    "Space"
).OnEvent("Click", AddSpace)

mygui.Show()

; --- Handlers ---

OnCharClick(btn, *)
{
    global shift, currentText, display, maxLen

    if (StrLen(currentText) >= maxLen)
        return

    char := btn.Orig

    if (shift)
    {
        if (char = "-")
            char := "_"
        else
            char := StrUpper(char)
    }
    else
    {
        char := StrLower(char)
    }

    currentText .= char
    display.Value := currentText
}

AddSpace(*)
{
    global currentText, display, maxLen

    if (StrLen(currentText) >= maxLen)
        return

    currentText .= " "
    display.Value := currentText
}

ToggleShift(*)
{
    global shift, buttons

    shift := !shift

    for btn in buttons
    {
        char := btn.Orig

        if (shift)
        {
            if (char = "-")
                btn.Text := "_"
            else
                btn.Text := StrUpper(char)
        }
        else
        {
            btn.Text := StrLower(char)
        }
    }
}

Backspace(*)
{
    global currentText, display

    if (StrLen(currentText) > 0)
    {
        currentText := SubStr(currentText, 1, -1)
        display.Value := currentText
    }
}

ClearText(*)
{
    global currentText, display

    currentText := ""
    display.Value := ""
}

SubmitText()
{
    global currentText, display, targetHwnd ; mygui

    if (currentText = "")
        return

    if (!targetHwnd)
    {
        MsgBox "No target HWND!"
        return
    }

    data := currentText
	size := (StrLen(data) + 1) * 2   ;Bytes , not chars

    cds := Buffer(A_PtrSize * 3)
    NumPut("UPtr", 1, cds, 0)
    NumPut("UPtr", size, cds, A_PtrSize)
    NumPut("UPtr", StrPtr(data), cds, A_PtrSize * 2)

    ; SendMessage(0x4A, 0, cds, , "ahk_id " targetHwnd)
	result := DllCall(
		"SendMessageW",
		"Ptr", targetHwnd,
		"UInt", 0x4A,        ; WM_COPYDATA
		"Ptr", 0,
		"Ptr", cds.Ptr,
		"Ptr"
	)
	; MsgBox "Result = " result

	ExitApp   
    ;currentText := ""
    ;display.Value := ""

    ;mygui.Hide()
}

OnCancel(*)
{
    global targetHwnd ; mygui

    if (targetHwnd)
    {
        cds := Buffer(A_PtrSize * 3)
        NumPut("UPtr", 2, cds, 0)             ; dwData = CANCEL
        NumPut("UPtr", 0, cds, A_PtrSize)     ; cbData = 0
        NumPut("UPtr", 0, cds, A_PtrSize*2)   ; lpData = NULL

        ; SendMessage(0x4A, 0, cds, , "ahk_id " targetHwnd)
		result := DllCall(
			"SendMessageW",
			"Ptr", targetHwnd,
			"UInt", 0x4A,        ; WM_COPYDATA
			"Ptr", 0,
			"Ptr", cds.Ptr,
			"Ptr"
		)
		; MsgBox "Result = " result
    }

	ExitApp
    ;mygui.Hide()   ;
}

mygui.OnEvent("Close", OnCancel)