package main

import (
	"fmt"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"
)

const lib_sdk = "sdk.dll"
const func_inject = "WxInitSDK"
const func_destroy = "WxDestroySDK"

var gbl_port int = 8001
var gbl_debug bool = true
var gbl_dll *syscall.DLL

func log(args ...interface{}) {
	fmt.Println("\033[1;7;32m[Inj]\033[0m", time.Now().Format("20060102_150405"), args)
}

/** 初始化. 加载动态库 */
func init() {
	log("Load dll:", lib_sdk)
	var err error
	gbl_dll, err = syscall.LoadDLL(lib_sdk)
	if err != nil { panic(err) }
}

/** 调用库接口 */
func call_func(fun_name string, title string) {
	log(title)
	// log("Find function:", fun_name, "in dll:", gbl_dll)
	fun, err := gbl_dll.FindProc(fun_name)
	if err != nil { panic(err) }

	// log("Call function:", fun)
	dbgUintptr := uintptr(0)
	if gbl_debug { dbgUintptr = uintptr(1) }
	ret, _e, errno := syscall.Syscall(fun.Addr(), dbgUintptr, 0, uintptr(gbl_port), 0)
	if ret != 0 {
		panic("Function " + fmt.Sprint(fun) + " run failed! return:" +
		fmt.Sprint(ret) + ", err:" + fmt.Sprint(_e) + ", errno:" + fmt.Sprint(errno))
	}
}

/** 监听并等待SIGINT信号 */
func waiting_signal() {
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	log("Is running, press Ctrl+C to quit.")
	<-sigChan
	log("Stopped!")
}

func show_help(ret int) {
	log("Usage:", os.Args[0], "[port [debug]]")
	os.Exit(ret)
}

func main() {
	log("### Inject SDK into WeChat ###")
	argc := len(os.Args)
	var err error
	if argc > 1 {
		gbl_port, err = strconv.Atoi(os.Args[1])
		if err != nil { show_help(1) }
	}
	if argc > 2 {
		gbl_debug, err = strconv.ParseBool(os.Args[2])
		if err != nil { show_help(1) }
	}
	log("Set sdk port:", gbl_port, "debug:", gbl_debug)

	start_at := time.Now()
	for {
		if func() bool {
			defer func() {
				if r := recover(); r != nil { // 注入失败时反复重试
					log("Get panic:", r, " Wait for retry...")
					time.Sleep(3 * time.Second)
				}
			}()
			call_func(func_inject, "Inject SDK...")
			return true
		}() { break }
	}
	log("SDK inject success. Time used:", time.Now().Sub(start_at).Seconds())

	waiting_signal()
	call_func(func_destroy, "SDK destroy")
	gbl_dll.Release()
}

