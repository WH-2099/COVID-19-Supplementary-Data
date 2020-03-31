#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'命令行输出颜色'

__author__ = 'WH-2099'


import os
import ctypes



def _posixPrintColorStr(string:str, foreColor:str, backColor:str, displayType:str):
    '''
    ANSI转义序列--适用于POSIX
    格式：\033[显示方式;前景色;背景色m
    说明：
    前景色            背景色           颜色
    ---------------------------------------
    30                40              黑色
    31                41              红色
    32                42              绿色
    33                43              黃色
    34                44              蓝色
    35                45              紫红色
    36                46              青蓝色
    37                47              白色
    显示方式           意义
    ---------------------------------------
    0                终端默认设置
    1                高亮显示
    4                使用下划线
    5                闪烁
    7                反白显示
    8                不可见
    '''
    if displayType:
        displayType = {'default':  '0',
                       'highlight':'1',
                       'underline':'4',
                       'twinkle':  '5',
                       'swap':     '7',
                       'invisible':'8'}.get(displayType, '0')
    if foreColor:
        foreColor = {'black': '30',
                     'red':   '31',
                     'green': '32',
                     'yellow':'33',
                     'blue':  '34',
                     'purple':'35',
                     'cyan':  '36',
                     'white': '37',
                     'default': ''}.get(foreColor, '')
    if backColor:
        backColor = {'black': '40',
                     'red':   '41',
                     'green': '42',
                     'yellow':'43',
                     'blue':  '44',
                     'purple':'45',
                     'cyan':  '46',
                     'white': '47',
                     'default': ''}.get(backColor, '')
    #filter是为了去除空字符串，防止生成连续的冒号';;'，连续冒号将使转义序列失效
    string = '\033[' + ';'.join(filter(None,(displayType, foreColor, backColor))) + 'm' + string + '\033[0m'
    print(string, end='', flush=True)



def _windowsPrintColorStr(string:str, foreColor:str, backColor:str, displayType:str):
    '''
    cmd32设置输出颜色--适用于windows(nt)
    利用SetConsoleTextAttribute函数
    靠一个字节的低四位控制前景色，高四位控制背景色
    即由2位十六进制组成，分别取0~f
    前一位指的是背景色，后一位指的是字体色
    组合使用[或]运算
    '''
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    #除默认颜色外，基本颜色相同，低四位前景色，高四位背景色
    SINGLE_COLOR = {'black': 0x0,
                    'blue':  0x1,
                    'green': 0x2,
                    'cyan':  0x3,
                    'red':   0x4,
                    'purple':0x5,
                    'yellow':0x6,
                    'white' :0x7,
                    'highlight':0x8}
    #前景色默认为white，背景色默认为black，即0x07
    defaultColor= 0x07
    foreColor = SINGLE_COLOR.get(foreColor, SINGLE_COLOR['white'])
    backColor = SINGLE_COLOR.get(backColor, SINGLE_COLOR['black'])
    #高亮处理
    if displayType == 'highlight':
        foreColor |= SINGLE_COLOR['highlight']
    if displayType == 'twinkle':
        backColor |= SINGLE_COLOR['highlight']
    #背景色需要左移四位
    backColor <<= 4
    color = foreColor | backColor
    ctypes.windll.kernel32.SetConsoleTextAttribute(std_out_handle, color)
    print(string, end='', flush=True)
    ctypes.windll.kernel32.SetConsoleTextAttribute(std_out_handle, defaultColor)

    

def printColorStr(string:str, foreColor:str='', backColor:str='', displayType:str=''):
    '''printColorStr(string:str, foreColor:str='', backColor:str='', displayType:str='')
    以指定颜色格式输出字符串，自动匹配平台
    string:要输出的字符串
    foreColor:前景色
    backColor:背景色
    displayType:显示类型

    Color：'black', 'blue', 'green', 'cyan', 'red', 'purple', 'yellow', 'white'
    displayType:'default', 'highlight', 'underline', 'twinkle', 'swap', 'invisible'
    
    ###displayType具体实现受限于终端及平台类型，可能并不生效
    ###但经测试highlight在各种情况下表现良好
    '''
    if os.name == 'nt':
        _windowsPrintColorStr(string, foreColor, backColor, displayType)
    elif os.name == 'posix':
        _posixPrintColorStr(string, foreColor, backColor, displayType)
    else:
        raise SystemError



if __name__ == '__main__':
    '输出全部支持效果'
    supportColor=('black', 'blue', 'green', 'cyan', 'red', 'purple', 'yellow', 'white')
    supportDisplayType=('default', 'highlight', 'underline', 'twinkle', 'swap', 'invisible')
    for displayType in supportDisplayType:
        print(f"{displayType:^30}")
        for foreColor in supportColor:
            for backColor in supportColor:
                Test=f"{foreColor[:1]}{backColor[:1]}{displayType[:1]}"
                printColorStr(Test, foreColor, backColor, displayType)
                print(' ', end='', flush=True)
            else:
                print()
        else:
            print()