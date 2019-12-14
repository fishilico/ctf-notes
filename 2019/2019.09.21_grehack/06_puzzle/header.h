typedef unsigned char u8;
typedef unsigned int u32;
typedef unsigned long u64;

struct TRANSPARENT_PT_LIST { // size 0x18, list of transparent points
    u32 y;
    u32 x;
    struct TRANSPARENT_PT_LIST *pNext;
    struct TRANSPARENT_PT_LIST *pPrev;
};

struct BITMAP { // Size 0x20; byte<dwCountOfBlocks>, byte<dwSizeOfABlock>, memblocks...
    u8 **pPixels; // bmp->pPixels[y][x]
    struct TRANSPARENT_PT_LIST *pTransparentPts_Head;
    u32 dwCountOfTransparentPts;
    u32 dwHeight;  // CountOfBlocks_height;
    u32 dwWidth;  // SizeOfABlock_width;
    u32 field_1c;
};

struct UNK_FCT_6046 { struct BITMAP bmp;};

struct ENC_TYPE_I_SUB { // Size 0x10; second field then the rectangle
    struct BITMAP *pBmp;
    u64 byte_from_file;
};

struct ENC_PART { // Size 0x30
    u8 type__1_for_I__2_for_L;
    u8 _field_00_pad[3];
    u32 field_04;
    u64 field_08;
    union ENC_PART_I_or_L {
        struct ENC_PART__I {
            u32 header_firstbyte;
            u32 header_secondbyte;
            struct ENC_TYPE_I_SUB *subpart_rect_and_attr;
            struct ENC_PART *child_left;
            struct ENC_PART *child_right;
        } i;
        struct ENC_PART__L {
            struct ENC_TYPE_I_SUB **pArrayRectangles;
            u32 dwCount;
        } l;
    } u;
};

struct ENC_TYPE_I { // Size 0x30
    u8 type__1_for_I__2_for_L;
    u8 _field_00_pad[3];
    u32 field_04;
    u64 field_08;
    u32 header_firstbyte_y;
    u32 header_secondbyte_x;
    struct ENC_TYPE_I_SUB *subpart_rect_and_attr;
    struct ENC_PART *child_left;
    struct ENC_PART *child_right;
};

struct ENC_TYPE_L { // Size 0x30
    u8 type__1_for_I__2_for_L;
    u8 _field_00_pad[3];
    u32 field_04;
    u64 field_08;
    struct ENC_TYPE_I_SUB **pArrayRectangles;
    u32 dwCount;
    u32 field_1c;
    u32 field_20;
    u32 field_24;
    u32 field_28;
    u32 field_2c;
};

struct SHA256_CTX { // Size 0x70
    u8 current_block64[0x40];
    u32 block_pos;
    u32 _field_17_padding;
    u64 number_bits_total;
    u32 H[8];
};
