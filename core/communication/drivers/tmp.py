void read(){
    get_header()
    get_addr()
    get_tail()
    //��֤��
    __decode_read_msg(byte_sequence,byte_deal)
    //����
}

void write(){
    get_header()
    get_addr()
    get_tail()
    //��֤��
    __encode_write_msg(byte_sequence,byte_deal)
    //����
}

void __decode_read_msg(byte_sequence,byte_deal){
    transform()
}

void __encode_write_msg(byte_sequence,byte_deal){
    inverse()
}