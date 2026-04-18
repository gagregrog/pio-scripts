"""
Pre-build script: reads tags.csv and generates include/TagMap.h.

tags.csv format (gitignored — do not commit):
    # comments and blank lines are ignored
    # ID is assigned by line position, starting at 1
    DE:AD:BE:EF:12:34:56
    AB:CD:EF:01:23:45

If tags.csv is absent, an empty TAG_MAP is generated so the build still works.
"""

Import("env")
import os


def parse_uid(uid_str):
    return [int(b, 16) for b in uid_str.strip().split(":")]


def gen_tagmap(project_dir):
    tags_path = os.path.join(project_dir, "tags.csv")
    entries = []
    if os.path.exists(tags_path):
        with open(tags_path) as f:
            tag_id = 1
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                entries.append((parse_uid(line), tag_id))
                tag_id += 1

    lines = [
        "#pragma once",
        "#include <stdint.h>",
        "",
        "// Auto-generated from tags.csv — do not edit",
        "",
        "struct TagEntry {",
        "    uint8_t uid[7];",
        "    uint8_t uidLen;",
        "    int id;",
        "};",
        "",
        "static const TagEntry TAG_MAP[] = {",
    ]
    for uid, tag_id in entries:
        byte_str = ", ".join("0x{:02X}".format(b) for b in uid)
        lines.append("    {{ {{{}}}, {}, {} }},".format(byte_str, len(uid), tag_id))
    lines += [
        "};",
        "",
        "static const int TAG_MAP_SIZE = sizeof(TAG_MAP) / sizeof(TAG_MAP[0]);",
        "",
    ]

    out_path = os.path.join(project_dir, "include", "TagMap.h")
    with open(out_path, "w") as f:
        f.write("\n".join(lines))

    print("[gen_tagmap] Generated TagMap.h with {} entr{}".format(
        len(entries), "y" if len(entries) == 1 else "ies"
    ))


gen_tagmap(env["PROJECT_DIR"])
