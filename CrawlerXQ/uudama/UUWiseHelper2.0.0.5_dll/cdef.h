#pragma once

#ifndef _UU_API_EXPORT
#define UUAPI extern "C" 
#else
#define UUAPI extern "C" _declspec(dllexport)
#endif

UUAPI void WINAPI uu_setSoftInfoA(LONG nSoftID, LPCSTR lpSoftKey);
UUAPI void WINAPI uu_setSoftInfoW(LONG nSoftID, LPCWSTR lpSoftKey);


UUAPI LONG WINAPI uu_loginA(LPCSTR lpUserName, LPCSTR lpPassword);
UUAPI LONG WINAPI uu_loginW(LPCWSTR lpUserName, LPCWSTR lpPassword);


UUAPI LONG WINAPI uu_reguserA (LPCSTR lpUserName, LPCSTR lpPassword, LONG nSoftID, LPCSTR lpSoftKey);
UUAPI LONG WINAPI uu_reguserW (LPCWSTR lpUserName, LPCWSTR lpPassword, LONG nSoftID, LPCWSTR lpSoftKey);

UUAPI LONG WINAPI uu_payA (LPCSTR lpUserName, LPCSTR lpCard, LONG nSoftID, LPCSTR lpSoftKey);
UUAPI LONG WINAPI uu_payW (LPCWSTR lpUserName, LPCWSTR lpCard, LONG nSoftID, LPCWSTR lpSoftKey);

UUAPI LONG WINAPI uu_recognizeByCodeTypeAndPathA (LPCSTR lpPicPath, LONG nCodeType, LPSTR pCodeResult);
UUAPI LONG WINAPI uu_recognizeByCodeTypeAndPathW (LPCWSTR lpPicPath, LONG nCodeType, LPWSTR pCodeResult);

UUAPI LONG WINAPI uu_recognizeByCodeTypeAndBytesA (CHAR pPicBytes[], LONG NumberOfBytes, LONG nCodeType, LPSTR pCodeResult);
UUAPI LONG WINAPI uu_recognizeByCodeTypeAndBytesW (CHAR pPicBytes[], LONG NumberOfBytes, LONG nCodeType, LPWSTR pCodeResult);

UUAPI LONG WINAPI uu_reportError(LONG nCodeID);


UUAPI LONG WINAPI uu_getScoreA (LPCSTR lpUserName, LPCSTR lpPassword);
UUAPI LONG WINAPI uu_getScoreW (LPCWSTR lpUserName, LPCWSTR lpPassword);


UUAPI void WINAPI uu_getResultA (LONG nCodeID, LPSTR pCodeResult);	
UUAPI void WINAPI uu_getResultW (LONG nCodeID, LPWSTR pCodeResult);	


UUAPI void WINAPI uu_setTimeOut (LONG nTimeOut);


UUAPI LONG WINAPI uu_recognizeScreenByCodeTypeA (LONG X, LONG Y, LONG nWidth, LONG nHeight, LONG nCodeType, LPSTR pCodeResult);
UUAPI LONG WINAPI uu_recognizeScreenByCodeTypeW (LONG X, LONG Y, LONG nWidth, LONG nHeight, LONG nCodeType, LPWSTR pCodeResult);


UUAPI LONG WINAPI uu_recognizeWndByTitleAndPosA (LPCSTR lpWndTitle, LONG X, LONG Y, LONG nWidth, LONG nHeight, LONG nCodeType, LPSTR pCodeResult);
UUAPI LONG WINAPI uu_recognizeWndByTitleAndPosW (LPCWSTR lpWndTitle, LONG X, LONG Y, LONG nWidth, LONG nHeight, LONG nCodeType, LPWSTR pCodeResult);

UUAPI LONG WINAPI uu_recognizeWndByHWndAndPosA (HWND hWnd, LONG X, LONG Y, LONG nWidth, LONG nHeight, LONG nCodeType, LPSTR pCodeResult);
UUAPI LONG WINAPI uu_recognizeWndByHWndAndPosW (HWND hWnd, LONG X, LONG Y, LONG nWidth, LONG nHeight, LONG nCodeType, LPWSTR pCodeResult);


UUAPI LONG WINAPI uu_UploadFileA (LPCSTR lpPicPath, LONG nCodeType);	
UUAPI LONG WINAPI uu_UploadFileW (LPCWSTR lpPicPath, LONG nCodeType);


UUAPI LONG WINAPI uu_UploadScreen(LONG X, LONG Y, LONG nWidth, LONG nHeight, LONG nCodeType);

UUAPI LONG WINAPI uu_recognizeByCodeTypeAndUrlA(LPCSTR lpstrUrl, LPCSTR lpstrInCookie, LONG nCodeType, LPSTR pCookieResult, LPSTR pCodeResult);
UUAPI LONG WINAPI uu_recognizeByCodeTypeAndUrlW(LPCWSTR lpstrUrl, LPCWSTR lpstrInCookie, LONG nCodeType, LPWSTR pCookieResult, LPWSTR pCodeResult);


//建议VB等不方便使用多线程语言使用
UUAPI HANDLE WINAPI uu_AsyncRecognizeByCodeTypeAndPathA (LPCSTR lpPicPath, LONG lCodeType, HANDLE hEvent);
UUAPI LONG WINAPI uu_CloseAsyncRecognizeHandle(HANDLE Handle);
UUAPI LONG WINAPI uu_GetAsyncRecognizeResultA(HANDLE Handle, LPSTR pCodeResult);

UUAPI LONG WINAPI uu_easyRecognizeFileA(LONG nSoftID, LPCSTR lpSoftKey, LPCSTR lpUserName, LPCSTR lpPassword, LPCSTR lpPicPath, LONG nCodeType, LPSTR pCodeResult);
UUAPI LONG WINAPI uu_easyRecognizeFileW(LONG nSoftID, LPCWSTR lpSoftKey, LPCWSTR lpUserName, LPCWSTR lpPassword, LPCWSTR lpPicPath, LONG nCodeType, LPWSTR pCodeResult);
UUAPI LONG WINAPI uu_easyRecognizeBytesA(LONG nSoftID, LPCSTR lpSoftKey, LPCSTR lpUserName, LPCSTR lpPassword, CHAR pPicBytes[], LONG NumberOfBytes, LONG nCodeType, LPSTR pCodeResult);
UUAPI LONG WINAPI uu_easyRecognizeBytesW(LONG nSoftID, LPCWSTR lpSoftKey, LPCWSTR lpUserName, LPCWSTR lpPassword, CHAR pPicBytes[], LONG NumberOfBytes, LONG nCodeType, LPWSTR pCodeResult);
UUAPI LONG WINAPI uu_easyRecognizeScreenA(LONG nSoftID, LPCSTR lpSoftKey, LPCSTR lpUserName, LPCSTR lpPassword, LONG X, LONG Y, LONG nWidth, LONG nHeight, LONG nCodeType, LPSTR pCodeResult);
UUAPI LONG WINAPI uu_easyRecognizeScreenW(LONG nSoftID, LPCWSTR lpSoftKey, LPCWSTR lpUserName, LPCWSTR lpPassword, LONG X, LONG Y, LONG nWidth, LONG nHeight, LONG nCodeType, LPWSTR pCodeResult);
UUAPI LONG WINAPI uu_easyRecognizeWndByTitleAndPosA(LONG nSoftID, LPCSTR lpSoftKey, LPCSTR lpUserName, LPCSTR lpPassword, LPCSTR lpWndTitle, LONG X, LONG Y, LONG nWidth, LONG nHeight, LONG nCodeType, LPSTR pCodeResult);
UUAPI LONG WINAPI uu_easyRecognizeWndByTitleAndPosW(LONG nSoftID, LPCWSTR lpSoftKey, LPCWSTR lpUserName, LPCWSTR lpPassword, LPCWSTR lpWndTitle, LONG X, LONG Y, LONG nWidth, LONG nHeight, LONG nCodeType, LPWSTR pCodeResult);
UUAPI LONG WINAPI uu_easyRecognizeWndByHWndAndPosA(LONG nSoftID, LPCSTR lpSoftKey, LPCSTR lpUserName, LPCSTR lpPassword, HWND hWnd, LONG X, LONG Y, LONG nWidth, LONG nHeight, LONG nCodeType, LPSTR pCodeResult);
UUAPI LONG WINAPI uu_easyRecognizeWndByHWndAndPosW(LONG nSoftID, LPCWSTR lpSoftKey, LPCWSTR lpUserName, LPCWSTR lpPassword, HWND hWnd, LONG X, LONG Y, LONG nWidth, LONG nHeight, LONG nCodeType, LPWSTR pCodeResult);
UUAPI LONG WINAPI uu_easyRecognizeUrlA(LONG nSoftID, LPCSTR lpSoftKey, LPCSTR lpUserName, LPCSTR lpPassword, LPCSTR lpstrUrl, LPCSTR lpstrInCookie, LONG nCodeType, LPSTR pCookieResult, LPSTR pCodeResult);
UUAPI LONG WINAPI uu_easyRecognizeUrlW(LONG nSoftID, LPCWSTR lpSoftKey, LPCWSTR lpUserName, LPCWSTR lpPassword, LPCWSTR lpstrUrl, LPCWSTR lpstrInCookie, LONG nCodeType, LPWSTR pCookieResult, LPWSTR pCodeResult);


UUAPI LONG WINAPI uu_SysCallOneParam(LONG CommandID, LONG Param);

UUAPI void WINAPI uu_CheckApiSignA(LONG nSoftID, LPCSTR lpSoftKey, LPCSTR lpGuid, LPCSTR lpFileMd5, LPCSTR lpFileCrc, LPSTR pCheckResult);
UUAPI void WINAPI uu_CheckApiSignW(LONG nSoftID, LPCWSTR lpSoftKey, LPCWSTR lpGuid, LPCWSTR lpFileMd5, LPCWSTR lpFileCrc, LPWSTR pCheckResult);