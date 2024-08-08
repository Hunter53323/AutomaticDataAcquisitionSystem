void read(){
    get_header()
    get_addr()
    get_tail()
    //验证等
    __decode_read_msg(byte_sequence,byte_deal)
    //其他
}

void write(){
    get_header()
    get_addr()
    get_tail()
    //验证等
    __encode_write_msg(byte_sequence,byte_deal)
    //其他
}

void __decode_read_msg(byte_sequence,byte_deal){
    transform()
}

void __encode_write_msg(byte_sequence,byte_deal){
    inverse()
}