#!/usr/bin/env python

def script(app, scene, resume):
    when = scene.when
    print('level')
    yield when.once(.3, resume)
    print('script')
    yield when.once(.3, resume)
    print('test')
    yield when.once(.3, resume)
    print('1')
    yield when.once(.3, resume)
    print('2')
    yield when.once(.3, resume)
    print('3')
    yield when.once(.3, resume)

