# Chapter appendix: Error Handling

> **中文标题**: 错误处理
> **页码范围**: 1063-1067
> **OCR 提取**: PaddleOCR-VL-1.5

---

<!-- Page 1063 -->

# Error Handling

Programmers should always check the error codes returned by system-level functions. There are many subtle ways that things can go wrong, and it only makes sense to use the status information that the kernel is able to provide us. Unfortunately, programmers are often reluctant to do error checking because it clutters their code, turning a single line of code into a multi-line conditional statement. Error checking is also confusing because different functions indicate errors in different ways.

We were faced with a similar problem when writing this text. On the one hand, we would like our code examples to be concise and simple to read. On the other hand, we do not want to give students the wrong impression that it is OK to skip error checking. To resolve these issues, we have adopted an approach based on error-handling wrappers that was pioneered by W. Richard Stevens in his network programming text [110].

The idea is that given some base system-level function foo, we define a wrapper function Foo with identical arguments, but with the first letter capitalized. The wrapper calls the base function and checks for errors. If it detects an error, the wrapper prints an informative message and terminates the process. Otherwise, it returns to the caller. Notice that if there are no errors, the wrapper behaves exactly like the base function. Put another way, if a program runs correctly with wrappers, it will run correctly if we render the first letter of each wrapper in lowercase and recompile.

The wrappers are packaged in a single source file (csapp.c) that is compiled and linked into each program. A separate header file (csapp.h) contains the function prototypes for the wrappers.

This appendix gives a tutorial on the different kinds of error handling in Unix systems and gives examples of the different styles of error-handling wrappers. Copies of the csapp.h and csapp.c files are available at the CS:APP Web site.

---

<!-- Page 1064 -->

## Coming in this systems

The systems-level function calls that we will encounter in this book use three different styles for returning errors: Unix-style, Posix-style, and GAI-style.

Functions such as fork and wait that were developed in the early days of Unix (as well as some older Posix functions) overload the function return value with both error codes and useful results. For example, when the Unix-style wait function encounters an error (e.g., there is no child process to reap), it returns -1 and sets the global variable errno to an error code that indicates the cause of the error. If wait completes successfully, then it returns the useful result, which is the PID of the reaped child. Unix-style error-handling code is typically of the following form:

if ((pid = wait(NULL)) < 0) {
    fprintf(stderr, "wait error: %s\n", strerror(errno));
    exit(0);
}

## Unix-Style Error Handling

The strerror function returns a text description for a particular value of  $ \text{errno} $.

## Posix-Style Error Handling

Many of the newer Posix functions such as Pthreads use the return value only to indicate success (zero) or failure (nonzero). Any useful results are returned in function arguments that are passed by reference. We refer to this approach as Posix-style error handling. For example, the Posix-style pthread_create function indicates success or failure with its return value and returns the ID of the newly created thread (the useful result) by reference in its first argument. Posix-style error-handling code is typically of the following form:

if ((retcode = pthread_create(&tid, NULL, thread, NULL))!= 0) {
    fprintf(stderr, "pthread_create error: %s\n", strerror(retcode));
    exit(0);
}

The strerror function returns a text description for a particular value of retcode.

## GAI-Style Error Handling

The getaddrinfo (GAI) and getnameinfo functions return zero on success and a nonzero value on failure. GAI error-handling code is typically of the following form:

if ((retcode = getaddrinfo(host, service, &hints, &result))!= 0) {
    fprintf(stderr, "getaddrinfo error: %s\n", gai_strerror(retcode));
    exit(0);
}

---

<!-- Page 1065 -->

of retcode.

## Summary of Error-Reporting Functions

Thoughout this book, we use the following error-reporting functions to accommodate different error-handling styles.

#include "csapp.h"

void unix_error(char *msg);
void posix_error(int code, char *msg);
void gai_error(int code, char *msg);
void app_error(char *msg);
Returns: nothing

As their names suggest, the unix_error, posix_error, and gai_error functions report Unix-style, Posix-style, and GAI-style errors and then terminate. The app_error function is included as a convenience for application errors. It simply prints its input and then terminates. Figure A.1 shows the code for the error-reporting functions.

### A.2 Error-Handling Wrappers

Here are some examples of the different error-handling wrappers.

Unix-style error-handling wrappers. Figure A.2 shows the wrapper for the Unix-style wait function. If the wait returns with an error, the wrapper prints an informative message and then exits. Otherwise, it returns a PID to the caller. Figure A.3 shows the wrapper for the Unix-style kill function. Notice that this function, unlike wait, returns void on success.

Posix-style error-handling wrappers. Figure A.4 shows the wrapper for the Posix-style pthread_detach function. Like most Posix-style functions, it does not overload useful results with error-return codes, so the wrapper returns void on success.

GAI-style error-handling wrappers. Figure A.5 shows the error-handling wrapper for the GAI-style getaddrinfo function.

---

<!-- Page 1066 -->

void unix_error(char *msg) /* Unix-style error */
{
    fprintf(stderr, "%s: %s\\n", msg, sterror(errno));
    exit(0);
}

void posix_error(int code, char *msg) /* Posix-style error */
{
    fprintf(stderr, "%s: %s\\n", msg, sterror(code));
    exit(0);
}

void gai_error(int code, char *msg) /* Getaddrinfo-style error */
{
    fprintf(stderr, "%s: %s\\n", msg, gai_strerror(code));
    exit(0);
}

void app_error(char *msg) /* Application error */
{
    fprintf(stderr, "%s\\n", msg);
    exit(0);
}

code/src/csapp.c

<div style="text-align: center;">Figure A.1 Error-reporting functions.</div>


code/src/csapp.c

1 pid_t Wait(int *status)
2 {
3     pid_t pid;
4
5     if ((pid = wait(status)) < 0)
6         unix_error("Wait error");
7     return pid;
8 }

code/src/csapp.c

<div style="text-align: center;">Figure A.2 Wrapper for Unix-style wait function.</div>

---

<!-- Page 1067 -->

void Kill(pid_t pid, int signum)
{
    int rc;

    if ((rc = kill(pid, signum)) < 0)
        unix_error("Kill error");
}
code/src/csapp.c

Figure A.3 Wrapper for Unix-style kill function.

void Pthread_detach(pthread_t tid) {
    int rc;

    if ((rc = pthread_detach(tid))!= 0)
        POSIX_ERROR(rc, "Pthread_detach error");
}
code/src/csapp.c

Figure A.4 Wrapper for Posix-style pthread_detach function.

void Getaddrinfo(const char *node, const char *service,
                           const struct addrinfo *hints, struct addrinfo **res)
{
    int rc;

    if ((rc = getaddrinfo(node, service, hints, res))!= 0)
        gai_error(rc, "Getaddrinfo error");
}
code/src/csapp.

Figure A.5 Wrapper for GAI-style getaddrinfo function.

---
