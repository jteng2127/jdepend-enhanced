# JDepend Enhanced

## usage

base command:

```bash
jdepend-enhanced <command>
```

generate report:

```bash
jdepend-enhanced report <classes dir> <report file path>
```

dive into package:

```bash
jdepend-enhanced dive <report file path>
```

`<classes dir>` default value is `/data`

`<report file path>` default value is `/data/report.txt`

for docker usage, you can mount your classes dir to `/data` and all will be fine.

## build

```bash
docker build -t jdepend-enhanced .
```

## run dev

```bash
docker build -t jdepend-enhanced --target dev .
docker run -it --rm -v %cd%/jdepend_enhanced:/app/jdepend_enhanced/jdepend_enhanced -v %cd%/classes:/data jdepend-enhanced bash
```

## run prod

```bash
docker build -t jdepend-enhanced --target prod .
docker run -it --rm -v %cd%/classes:/data jdepend-enhanced <command>
```