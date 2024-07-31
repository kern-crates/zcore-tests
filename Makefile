# Makefile for zcore test
ARCH ?= x86_64

zircon-core-test-libos:
	python3 zircon_core_test.py --libos #[ --fast --no-failed]

zircon-core-test:
# make zircon-init: Pull prebuilt images
	python3 zircon_core_test.py #[--fast]

libc-test:
ifeq ($(ARCH), x86_64)
	@[ -e ../rootfs/$(ARCH)/libc-test ] || \
		git clone https://github.com/kern-crates/libc-test.git --depth 1 ../rootfs/$(ARCH)/libc-test

	cd ../rootfs/x86_64/libc-test && cp config.mak.def config.mak && echo 'CC := musl-gcc' >> config.mak && make -j
#   cd ../rootfs/$(ARCH)/libc-test && cp libc-test/functional/tls_align-static.exe src/functional/tls_align-static.exe # why copy this ?
endif

linux-libc-test-libos: test-dep image libc-test 
# x86_64 rootfs/libos
	cp -rf ../rootfs/x86_64/libc-test ../rootfs/libos/libc-test
	python3 linux_libc_test.py --libos #[--fast]

linux-libc-test-baremetal: test-dep image libc-test
	python3 linux_libc_test-qemu.py --arch $(ARCH) # --fast

linux-other-test-baremetal: test-dep image
	python3 linux_other_test.py --arch $(ARCH) # --fast

.PHONY: test-dep image

image:
	cd ../ && make image ARCH=$(ARCH)

test-dep:
# sudo apt-get install -y ninja-build
	pip3 install -r requirements.txt