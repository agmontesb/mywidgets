# -*- coding: utf-8 -*-
# Ported from:
# https://github.com/aosp-mirror/platform_frameworks_base/blob/master/libs/androidfw/LocaleDataTables.cpp
#

SCRIPT_CODES = [
    'Ahom', # 0
    'Arab', # 1
    'Armi', # 2
    'Armn', # 3
    'Avst', # 4
    'Bamu', # 5
    'Bass', # 6
    'Beng', # 7
    'Brah', # 8
    'Cans', # 9
    'Cari', # 10
    'Cham', # 11
    'Cher', # 12
    'Copt', # 13
    'Cprt', # 14
    'Cyrl', # 15
    'Deva', # 16
    'Egyp', # 17
    'Ethi', # 18
    'Geor', # 19
    'Goth', # 20
    'Grek', # 21
    'Gujr', # 22
    'Guru', # 23
    'Hans', # 24
    'Hant', # 25
    'Hatr', # 26
    'Hebr', # 27
    'Hluw', # 28
    'Hmng', # 29
    'Ital', # 30
    'Jpan', # 31
    'Kali', # 32
    'Kana', # 33
    'Khar', # 34
    'Khmr', # 35
    'Knda', # 36
    'Kore', # 37
    'Lana', # 38
    'Laoo', # 39
    'Latn', # 40
    'Lepc', # 41
    'Lina', # 42
    'Lisu', # 43
    'Lyci', # 44
    'Lydi', # 45
    'Mand', # 46
    'Mani', # 47
    'Merc', # 48
    'Mlym', # 49
    'Mong', # 50
    'Mroo', # 51
    'Mymr', # 52
    'Narb', # 53
    'Nkoo', # 54
    'Ogam', # 55
    'Orkh', # 56
    'Orya', # 57
    'Osge', # 58
    'Pauc', # 59
    'Phli', # 60
    'Phnx', # 61
    'Plrd', # 62
    'Prti', # 63
    'Runr', # 64
    'Samr', # 65
    'Sarb', # 66
    'Saur', # 67
    'Sgnw', # 68
    'Sinh', # 69
    'Sora', # 70
    'Syrc', # 71
    'Tale', # 72
    'Talu', # 73
    'Taml', # 74
    'Tang', # 75
    'Tavt', # 76
    'Telu', # 77
    'Tfng', # 78
    'Thaa', # 79
    'Thai', # 80
    'Tibt', # 81
    'Ugar', # 82
    'Vaii', # 83
    'Xpeo', # 84
    'Xsux', # 85
    'Yiii', # 86
    '~~~A', # 87
    '~~~B', # 88
]

LIKELY_SCRIPTS = dict([
    (0x61610000, 40), #  aa -> Latn
    (0xA0000000, 40), #  aai -> Latn
    (0xA8000000, 40), #  aak -> Latn
    (0xD0000000, 40), #  aau -> Latn
    (0x61620000, 15), #  ab -> Cyrl
    (0xA0200000, 40), #  abi -> Latn
    (0xC4200000, 40), #  abr -> Latn
    (0xCC200000, 40), #  abt -> Latn
    (0xE0200000, 40), #  aby -> Latn
    (0x8C400000, 40), #  acd -> Latn
    (0x90400000, 40), #  ace -> Latn
    (0x9C400000, 40), #  ach -> Latn
    (0x80600000, 40), #  ada -> Latn
    (0x90600000, 40), #  ade -> Latn
    (0xA4600000, 40), #  adj -> Latn
    (0xE0600000, 15), #  ady -> Cyrl
    (0xE4600000, 40), #  adz -> Latn
    (0x61650000,  4), #  ae -> Avst
    (0x84800000,  1), #  aeb -> Arab
    (0xE0800000, 40), #  aey -> Latn
    (0x61660000, 40), #  af -> Latn
    (0x88C00000, 40), #  agc -> Latn
    (0x8CC00000, 40), #  agd -> Latn
    (0x98C00000, 40), #  agg -> Latn
    (0xB0C00000, 40), #  agm -> Latn
    (0xB8C00000, 40), #  ago -> Latn
    (0xC0C00000, 40), #  agq -> Latn
    (0x80E00000, 40), #  aha -> Latn
    (0xACE00000, 40), #  ahl -> Latn
    (0xB8E00000,  0), #  aho -> Ahom
    (0x99200000, 40), #  ajg -> Latn
    (0x616B0000, 40), #  ak -> Latn
    (0xA9400000, 85), #  akk -> Xsux
    (0x81600000, 40), #  ala -> Latn
    (0xA1600000, 40), #  ali -> Latn
    (0xB5600000, 40), #  aln -> Latn
    (0xCD600000, 15), #  alt -> Cyrl
    (0x616D0000, 18), #  am -> Ethi
    (0xB1800000, 40), #  amm -> Latn
    (0xB5800000, 40), #  amn -> Latn
    (0xB9800000, 40), #  amo -> Latn
    (0xBD800000, 40), #  amp -> Latn
    (0x89A00000, 40), #  anc -> Latn
    (0xA9A00000, 40), #  ank -> Latn
    (0xB5A00000, 40), #  ann -> Latn
    (0xE1A00000, 40), #  any -> Latn
    (0xA5C00000, 40), #  aoj -> Latn
    (0xB1C00000, 40), #  aom -> Latn
    (0xE5C00000, 40), #  aoz -> Latn
    (0x89E00000,  1), #  apc -> Arab
    (0x8DE00000,  1), #  apd -> Arab
    (0x91E00000, 40), #  ape -> Latn
    (0xC5E00000, 40), #  apr -> Latn
    (0xC9E00000, 40), #  aps -> Latn
    (0xE5E00000, 40), #  apz -> Latn
    (0x61720000,  1), #  ar -> Arab
    (0x61725842, 88), #  ar-XB -> ~~~B
    (0x8A200000,  2), #  arc -> Armi
    (0x9E200000, 40), #  arh -> Latn
    (0xB6200000, 40), #  arn -> Latn
    (0xBA200000, 40), #  aro -> Latn
    (0xC2200000,  1), #  arq -> Arab
    (0xE2200000,  1), #  ary -> Arab
    (0xE6200000,  1), #  arz -> Arab
    (0x61730000,  7), #  as -> Beng
    (0x82400000, 40), #  asa -> Latn
    (0x92400000, 68), #  ase -> Sgnw
    (0x9A400000, 40), #  asg -> Latn
    (0xBA400000, 40), #  aso -> Latn
    (0xCE400000, 40), #  ast -> Latn
    (0x82600000, 40), #  ata -> Latn
    (0x9A600000, 40), #  atg -> Latn
    (0xA6600000, 40), #  atj -> Latn
    (0xE2800000, 40), #  auy -> Latn
    (0x61760000, 15), #  av -> Cyrl
    (0xAEA00000,  1), #  avl -> Arab
    (0xB6A00000, 40), #  avn -> Latn
    (0xCEA00000, 40), #  avt -> Latn
    (0xD2A00000, 40), #  avu -> Latn
    (0x82C00000, 16), #  awa -> Deva
    (0x86C00000, 40), #  awb -> Latn
    (0xBAC00000, 40), #  awo -> Latn
    (0xDEC00000, 40), #  awx -> Latn
    (0x61790000, 40), #  ay -> Latn
    (0x87000000, 40), #  ayb -> Latn
    (0x617A0000, 40), #  az -> Latn
    (0x617A4951,  1), #  az-IQ -> Arab
    (0x617A4952,  1), #  az-IR -> Arab
    (0x617A5255, 15), #  az-RU -> Cyrl
    (0x62610000, 15), #  ba -> Cyrl
    (0xAC010000,  1), #  bal -> Arab
    (0xB4010000, 40), #  ban -> Latn
    (0xBC010000, 16), #  bap -> Deva
    (0xC4010000, 40), #  bar -> Latn
    (0xC8010000, 40), #  bas -> Latn
    (0xD4010000, 40), #  bav -> Latn
    (0xDC010000,  5), #  bax -> Bamu
    (0x80210000, 40), #  bba -> Latn
    (0x84210000, 40), #  bbb -> Latn
    (0x88210000, 40), #  bbc -> Latn
    (0x8C210000, 40), #  bbd -> Latn
    (0xA4210000, 40), #  bbj -> Latn
    (0xBC210000, 40), #  bbp -> Latn
    (0xC4210000, 40), #  bbr -> Latn
    (0x94410000, 40), #  bcf -> Latn
    (0x9C410000, 40), #  bch -> Latn
    (0xA0410000, 40), #  bci -> Latn
    (0xB0410000, 40), #  bcm -> Latn
    (0xB4410000, 40), #  bcn -> Latn
    (0xB8410000, 40), #  bco -> Latn
    (0xC0410000, 18), #  bcq -> Ethi
    (0xD0410000, 40), #  bcu -> Latn
    (0x8C610000, 40), #  bdd -> Latn
    (0x62650000, 15), #  be -> Cyrl
    (0x94810000, 40), #  bef -> Latn
    (0x9C810000, 40), #  beh -> Latn
    (0xA4810000,  1), #  bej -> Arab
    (0xB0810000, 40), #  bem -> Latn
    (0xCC810000, 40), #  bet -> Latn
    (0xD8810000, 40), #  bew -> Latn
    (0xDC810000, 40), #  bex -> Latn
    (0xE4810000, 40), #  bez -> Latn
    (0x8CA10000, 40), #  bfd -> Latn
    (0xC0A10000, 74), #  bfq -> Taml
    (0xCCA10000,  1), #  bft -> Arab
    (0xE0A10000, 16), #  bfy -> Deva
    (0x62670000, 15), #  bg -> Cyrl
    (0x88C10000, 16), #  bgc -> Deva
    (0xB4C10000,  1), #  bgn -> Arab
    (0xDCC10000, 21), #  bgx -> Grek
    (0x84E10000, 16), #  bhb -> Deva
    (0x98E10000, 40), #  bhg -> Latn
    (0xA0E10000, 16), #  bhi -> Deva
    (0xA8E10000, 40), #  bhk -> Latn
    (0xACE10000, 40), #  bhl -> Latn
    (0xB8E10000, 16), #  bho -> Deva
    (0xE0E10000, 40), #  bhy -> Latn
    (0x62690000, 40), #  bi -> Latn
    (0x85010000, 40), #  bib -> Latn
    (0x99010000, 40), #  big -> Latn
    (0xA9010000, 40), #  bik -> Latn
    (0xB1010000, 40), #  bim -> Latn
    (0xB5010000, 40), #  bin -> Latn
    (0xB9010000, 40), #  bio -> Latn
    (0xC1010000, 40), #  biq -> Latn
    (0x9D210000, 40), #  bjh -> Latn
    (0xA1210000, 18), #  bji -> Ethi
    (0xA5210000, 16), #  bjj -> Deva
    (0xB5210000, 40), #  bjn -> Latn
    (0xB9210000, 40), #  bjo -> Latn
    (0xC5210000, 40), #  bjr -> Latn
    (0xE5210000, 40), #  bjz -> Latn
    (0x89410000, 40), #  bkc -> Latn
    (0xB1410000, 40), #  bkm -> Latn
    (0xC1410000, 40), #  bkq -> Latn
    (0xD1410000, 40), #  bku -> Latn
    (0xD5410000, 40), #  bkv -> Latn
    (0xCD610000, 76), #  blt -> Tavt
    (0x626D0000, 40), #  bm -> Latn
    (0x9D810000, 40), #  bmh -> Latn
    (0xA9810000, 40), #  bmk -> Latn
    (0xC1810000, 40), #  bmq -> Latn
    (0xD1810000, 40), #  bmu -> Latn
    (0x626E0000,  7), #  bn -> Beng
    (0x99A10000, 40), #  bng -> Latn
    (0xB1A10000, 40), #  bnm -> Latn
    (0xBDA10000, 40), #  bnp -> Latn
    (0x626F0000, 81), #  bo -> Tibt
    (0xA5C10000, 40), #  boj -> Latn
    (0xB1C10000, 40), #  bom -> Latn
    (0xB5C10000, 40), #  bon -> Latn
    (0xE1E10000,  7), #  bpy -> Beng
    (0x8A010000, 40), #  bqc -> Latn
    (0xA2010000,  1), #  bqi -> Arab
    (0xBE010000, 40), #  bqp -> Latn
    (0xD6010000, 40), #  bqv -> Latn
    (0x62720000, 40), #  br -> Latn
    (0x82210000, 16), #  bra -> Deva
    (0x9E210000,  1), #  brh -> Arab
    (0xDE210000, 16), #  brx -> Deva
    (0xE6210000, 40), #  brz -> Latn
    (0x62730000, 40), #  bs -> Latn
    (0xA6410000, 40), #  bsj -> Latn
    (0xC2410000,  6), #  bsq -> Bass
    (0xCA410000, 40), #  bss -> Latn
    (0xCE410000, 18), #  bst -> Ethi
    (0xBA610000, 40), #  bto -> Latn
    (0xCE610000, 40), #  btt -> Latn
    (0xD6610000, 16), #  btv -> Deva
    (0x82810000, 15), #  bua -> Cyrl
    (0x8A810000, 40), #  buc -> Latn
    (0x8E810000, 40), #  bud -> Latn
    (0x9A810000, 40), #  bug -> Latn
    (0xAA810000, 40), #  buk -> Latn
    (0xB2810000, 40), #  bum -> Latn
    (0xBA810000, 40), #  buo -> Latn
    (0xCA810000, 40), #  bus -> Latn
    (0xD2810000, 40), #  buu -> Latn
    (0x86A10000, 40), #  bvb -> Latn
    (0x8EC10000, 40), #  bwd -> Latn
    (0xC6C10000, 40), #  bwr -> Latn
    (0x9EE10000, 40), #  bxh -> Latn
    (0x93010000, 40), #  bye -> Latn
    (0xB7010000, 18), #  byn -> Ethi
    (0xC7010000, 40), #  byr -> Latn
    (0xCB010000, 40), #  bys -> Latn
    (0xD7010000, 40), #  byv -> Latn
    (0xDF010000, 40), #  byx -> Latn
    (0x83210000, 40), #  bza -> Latn
    (0x93210000, 40), #  bze -> Latn
    (0x97210000, 40), #  bzf -> Latn
    (0x9F210000, 40), #  bzh -> Latn
    (0xDB210000, 40), #  bzw -> Latn
    (0x63610000, 40), #  ca -> Latn
    (0xB4020000, 40), #  can -> Latn
    (0xA4220000, 40), #  cbj -> Latn
    (0x9C420000, 40), #  cch -> Latn
    (0xBC420000,  7), #  ccp -> Beng
    (0x63650000, 15), #  ce -> Cyrl
    (0x84820000, 40), #  ceb -> Latn
    (0x80A20000, 40), #  cfa -> Latn
    (0x98C20000, 40), #  cgg -> Latn
    (0x63680000, 40), #  ch -> Latn
    (0xA8E20000, 40), #  chk -> Latn
    (0xB0E20000, 15), #  chm -> Cyrl
    (0xB8E20000, 40), #  cho -> Latn
    (0xBCE20000, 40), #  chp -> Latn
    (0xC4E20000, 12), #  chr -> Cher
    (0x81220000,  1), #  cja -> Arab
    (0xB1220000, 11), #  cjm -> Cham
    (0xD5220000, 40), #  cjv -> Latn
    (0x85420000,  1), #  ckb -> Arab
    (0xAD420000, 40), #  ckl -> Latn
    (0xB9420000, 40), #  cko -> Latn
    (0xE1420000, 40), #  cky -> Latn
    (0x81620000, 40), #  cla -> Latn
    (0x91820000, 40), #  cme -> Latn
    (0x636F0000, 40), #  co -> Latn
    (0xBDC20000, 13), #  cop -> Copt
    (0xC9E20000, 40), #  cps -> Latn
    (0x63720000,  9), #  cr -> Cans
    (0xA6220000,  9), #  crj -> Cans
    (0xAA220000,  9), #  crk -> Cans
    (0xAE220000,  9), #  crl -> Cans
    (0xB2220000,  9), #  crm -> Cans
    (0xCA220000, 40), #  crs -> Latn
    (0x63730000, 40), #  cs -> Latn
    (0x86420000, 40), #  csb -> Latn
    (0xDA420000,  9), #  csw -> Cans
    (0x8E620000, 59), #  ctd -> Pauc
    (0x63750000, 15), #  cu -> Cyrl
    (0x63760000, 15), #  cv -> Cyrl
    (0x63790000, 40), #  cy -> Latn
    (0x64610000, 40), #  da -> Latn
    (0x8C030000, 40), #  dad -> Latn
    (0x94030000, 40), #  daf -> Latn
    (0x98030000, 40), #  dag -> Latn
    (0x9C030000, 40), #  dah -> Latn
    (0xA8030000, 40), #  dak -> Latn
    (0xC4030000, 15), #  dar -> Cyrl
    (0xD4030000, 40), #  dav -> Latn
    (0x8C230000, 40), #  dbd -> Latn
    (0xC0230000, 40), #  dbq -> Latn
    (0x88430000,  1), #  dcc -> Arab
    (0xB4630000, 40), #  ddn -> Latn
    (0x64650000, 40), #  de -> Latn
    (0x8C830000, 40), #  ded -> Latn
    (0xB4830000, 40), #  den -> Latn
    (0x80C30000, 40), #  dga -> Latn
    (0x9CC30000, 40), #  dgh -> Latn
    (0xA0C30000, 40), #  dgi -> Latn
    (0xACC30000,  1), #  dgl -> Arab
    (0xC4C30000, 40), #  dgr -> Latn
    (0xE4C30000, 40), #  dgz -> Latn
    (0x81030000, 40), #  dia -> Latn
    (0x91230000, 40), #  dje -> Latn
    (0xA5A30000, 40), #  dnj -> Latn
    (0x85C30000, 40), #  dob -> Latn
    (0xA1C30000,  1), #  doi -> Arab
    (0xBDC30000, 40), #  dop -> Latn
    (0xD9C30000, 40), #  dow -> Latn
    (0xA2230000, 40), #  dri -> Latn
    (0xCA230000, 18), #  drs -> Ethi
    (0x86430000, 40), #  dsb -> Latn
    (0xB2630000, 40), #  dtm -> Latn
    (0xBE630000, 40), #  dtp -> Latn
    (0xCA630000, 40), #  dts -> Latn
    (0xE2630000, 16), #  dty -> Deva
    (0x82830000, 40), #  dua -> Latn
    (0x8A830000, 40), #  duc -> Latn
    (0x8E830000, 40), #  dud -> Latn
    (0x9A830000, 40), #  dug -> Latn
    (0x64760000, 79), #  dv -> Thaa
    (0x82A30000, 40), #  dva -> Latn
    (0xDAC30000, 40), #  dww -> Latn
    (0xBB030000, 40), #  dyo -> Latn
    (0xD3030000, 40), #  dyu -> Latn
    (0x647A0000, 81), #  dz -> Tibt
    (0x9B230000, 40), #  dzg -> Latn
    (0xD0240000, 40), #  ebu -> Latn
    (0x65650000, 40), #  ee -> Latn
    (0xA0A40000, 40), #  efi -> Latn
    (0xACC40000, 40), #  egl -> Latn
    (0xE0C40000, 17), #  egy -> Egyp
    (0xE1440000, 32), #  eky -> Kali
    (0x656C0000, 21), #  el -> Grek
    (0x81840000, 40), #  ema -> Latn
    (0xA1840000, 40), #  emi -> Latn
    (0x656E0000, 40), #  en -> Latn
    (0x656E5841, 87), #  en-XA -> ~~~A
    (0xB5A40000, 40), #  enn -> Latn
    (0xC1A40000, 40), #  enq -> Latn
    (0x656F0000, 40), #  eo -> Latn
    (0xA2240000, 40), #  eri -> Latn
    (0x65730000, 40), #  es -> Latn
    (0xD2440000, 40), #  esu -> Latn
    (0x65740000, 40), #  et -> Latn
    (0xC6640000, 40), #  etr -> Latn
    (0xCE640000, 30), #  ett -> Ital
    (0xD2640000, 40), #  etu -> Latn
    (0xDE640000, 40), #  etx -> Latn
    (0x65750000, 40), #  eu -> Latn
    (0xBAC40000, 40), #  ewo -> Latn
    (0xCEE40000, 40), #  ext -> Latn
    (0x66610000,  1), #  fa -> Arab
    (0x80050000, 40), #  faa -> Latn
    (0x84050000, 40), #  fab -> Latn
    (0x98050000, 40), #  fag -> Latn
    (0xA0050000, 40), #  fai -> Latn
    (0xB4050000, 40), #  fan -> Latn
    (0x66660000, 40), #  ff -> Latn
    (0xA0A50000, 40), #  ffi -> Latn
    (0xB0A50000, 40), #  ffm -> Latn
    (0x66690000, 40), #  fi -> Latn
    (0x81050000,  1), #  fia -> Arab
    (0xAD050000, 40), #  fil -> Latn
    (0xCD050000, 40), #  fit -> Latn
    (0x666A0000, 40), #  fj -> Latn
    (0xC5650000, 40), #  flr -> Latn
    (0xBD850000, 40), #  fmp -> Latn
    (0x666F0000, 40), #  fo -> Latn
    (0x8DC50000, 40), #  fod -> Latn
    (0xB5C50000, 40), #  fon -> Latn
    (0xC5C50000, 40), #  for -> Latn
    (0x91E50000, 40), #  fpe -> Latn
    (0xCA050000, 40), #  fqs -> Latn
    (0x66720000, 40), #  fr -> Latn
    (0x8A250000, 40), #  frc -> Latn
    (0xBE250000, 40), #  frp -> Latn
    (0xC6250000, 40), #  frr -> Latn
    (0xCA250000, 40), #  frs -> Latn
    (0x86850000,  1), #  fub -> Arab
    (0x8E850000, 40), #  fud -> Latn
    (0x92850000, 40), #  fue -> Latn
    (0x96850000, 40), #  fuf -> Latn
    (0x9E850000, 40), #  fuh -> Latn
    (0xC2850000, 40), #  fuq -> Latn
    (0xC6850000, 40), #  fur -> Latn
    (0xD6850000, 40), #  fuv -> Latn
    (0xE2850000, 40), #  fuy -> Latn
    (0xC6A50000, 40), #  fvr -> Latn
    (0x66790000, 40), #  fy -> Latn
    (0x67610000, 40), #  ga -> Latn
    (0x80060000, 40), #  gaa -> Latn
    (0x94060000, 40), #  gaf -> Latn
    (0x98060000, 40), #  gag -> Latn
    (0x9C060000, 40), #  gah -> Latn
    (0xA4060000, 40), #  gaj -> Latn
    (0xB0060000, 40), #  gam -> Latn
    (0xB4060000, 24), #  gan -> Hans
    (0xD8060000, 40), #  gaw -> Latn
    (0xE0060000, 40), #  gay -> Latn
    (0x94260000, 40), #  gbf -> Latn
    (0xB0260000, 16), #  gbm -> Deva
    (0xE0260000, 40), #  gby -> Latn
    (0xE4260000,  1), #  gbz -> Arab
    (0xC4460000, 40), #  gcr -> Latn
    (0x67640000, 40), #  gd -> Latn
    (0x90660000, 40), #  gde -> Latn
    (0xB4660000, 40), #  gdn -> Latn
    (0xC4660000, 40), #  gdr -> Latn
    (0x84860000, 40), #  geb -> Latn
    (0xA4860000, 40), #  gej -> Latn
    (0xAC860000, 40), #  gel -> Latn
    (0xE4860000, 18), #  gez -> Ethi
    (0xA8A60000, 40), #  gfk -> Latn
    (0xB4C60000, 16), #  ggn -> Deva
    (0xC8E60000, 40), #  ghs -> Latn
    (0xAD060000, 40), #  gil -> Latn
    (0xB1060000, 40), #  gim -> Latn
    (0xA9260000,  1), #  gjk -> Arab
    (0xB5260000, 40), #  gjn -> Latn
    (0xD1260000,  1), #  gju -> Arab
    (0xB5460000, 40), #  gkn -> Latn
    (0xBD460000, 40), #  gkp -> Latn
    (0x676C0000, 40), #  gl -> Latn
    (0xA9660000,  1), #  glk -> Arab
    (0xB1860000, 40), #  gmm -> Latn
    (0xD5860000, 18), #  gmv -> Ethi
    (0x676E0000, 40), #  gn -> Latn
    (0x8DA60000, 40), #  gnd -> Latn
    (0x99A60000, 40), #  gng -> Latn
    (0x8DC60000, 40), #  god -> Latn
    (0x95C60000, 18), #  gof -> Ethi
    (0xA1C60000, 40), #  goi -> Latn
    (0xB1C60000, 16), #  gom -> Deva
    (0xB5C60000, 77), #  gon -> Telu
    (0xC5C60000, 40), #  gor -> Latn
    (0xC9C60000, 40), #  gos -> Latn
    (0xCDC60000, 20), #  got -> Goth
    (0x8A260000, 14), #  grc -> Cprt
    (0xCE260000,  7), #  grt -> Beng
    (0xDA260000, 40), #  grw -> Latn
    (0xDA460000, 40), #  gsw -> Latn
    (0x67750000, 22), #  gu -> Gujr
    (0x86860000, 40), #  gub -> Latn
    (0x8A860000, 40), #  guc -> Latn
    (0x8E860000, 40), #  gud -> Latn
    (0xC6860000, 40), #  gur -> Latn
    (0xDA860000, 40), #  guw -> Latn
    (0xDE860000, 40), #  gux -> Latn
    (0xE6860000, 40), #  guz -> Latn
    (0x67760000, 40), #  gv -> Latn
    (0x96A60000, 40), #  gvf -> Latn
    (0xC6A60000, 16), #  gvr -> Deva
    (0xCAA60000, 40), #  gvs -> Latn
    (0x8AC60000,  1), #  gwc -> Arab
    (0xA2C60000, 40), #  gwi -> Latn
    (0xCEC60000,  1), #  gwt -> Arab
    (0xA3060000, 40), #  gyi -> Latn
    (0x68610000, 40), #  ha -> Latn
    (0x6861434D,  1), #  ha-CM -> Arab
    (0x68615344,  1), #  ha-SD -> Arab
    (0x98070000, 40), #  hag -> Latn
    (0xA8070000, 24), #  hak -> Hans
    (0xB0070000, 40), #  ham -> Latn
    (0xD8070000, 40), #  haw -> Latn
    (0xE4070000,  1), #  haz -> Arab
    (0x84270000, 40), #  hbb -> Latn
    (0xE0670000, 18), #  hdy -> Ethi
    (0x68650000, 27), #  he -> Hebr
    (0xE0E70000, 40), #  hhy -> Latn
    (0x68690000, 16), #  hi -> Deva
    (0x81070000, 40), #  hia -> Latn
    (0x95070000, 40), #  hif -> Latn
    (0x99070000, 40), #  hig -> Latn
    (0x9D070000, 40), #  hih -> Latn
    (0xAD070000, 40), #  hil -> Latn
    (0x81670000, 40), #  hla -> Latn
    (0xD1670000, 28), #  hlu -> Hluw
    (0x8D870000, 62), #  hmd -> Plrd
    (0xCD870000, 40), #  hmt -> Latn
    (0x8DA70000,  1), #  hnd -> Arab
    (0x91A70000, 16), #  hne -> Deva
    (0xA5A70000, 29), #  hnj -> Hmng
    (0xB5A70000, 40), #  hnn -> Latn
    (0xB9A70000,  1), #  hno -> Arab
    (0x686F0000, 40), #  ho -> Latn
    (0x89C70000, 16), #  hoc -> Deva
    (0xA5C70000, 16), #  hoj -> Deva
    (0xCDC70000, 40), #  hot -> Latn
    (0x68720000, 40), #  hr -> Latn
    (0x86470000, 40), #  hsb -> Latn
    (0xB6470000, 24), #  hsn -> Hans
    (0x68740000, 40), #  ht -> Latn
    (0x68750000, 40), #  hu -> Latn
    (0xA2870000, 40), #  hui -> Latn
    (0x68790000,  3), #  hy -> Armn
    (0x687A0000, 40), #  hz -> Latn
    (0x69610000, 40), #  ia -> Latn
    (0xB4080000, 40), #  ian -> Latn
    (0xC4080000, 40), #  iar -> Latn
    (0x80280000, 40), #  iba -> Latn
    (0x84280000, 40), #  ibb -> Latn
    (0xE0280000, 40), #  iby -> Latn
    (0x80480000, 40), #  ica -> Latn
    (0x9C480000, 40), #  ich -> Latn
    (0x69640000, 40), #  id -> Latn
    (0x8C680000, 40), #  idd -> Latn
    (0xA0680000, 40), #  idi -> Latn
    (0xD0680000, 40), #  idu -> Latn
    (0x69670000, 40), #  ig -> Latn
    (0x84C80000, 40), #  igb -> Latn
    (0x90C80000, 40), #  ige -> Latn
    (0x69690000, 86), #  ii -> Yiii
    (0xA5280000, 40), #  ijj -> Latn
    (0x696B0000, 40), #  ik -> Latn
    (0xA9480000, 40), #  ikk -> Latn
    (0xCD480000, 40), #  ikt -> Latn
    (0xD9480000, 40), #  ikw -> Latn
    (0xDD480000, 40), #  ikx -> Latn
    (0xB9680000, 40), #  ilo -> Latn
    (0xB9880000, 40), #  imo -> Latn
    (0x696E0000, 40), #  in -> Latn
    (0x9DA80000, 15), #  inh -> Cyrl
    (0xD1C80000, 40), #  iou -> Latn
    (0xA2280000, 40), #  iri -> Latn
    (0x69730000, 40), #  is -> Latn
    (0x69740000, 40), #  it -> Latn
    (0x69750000,  9), #  iu -> Cans
    (0x69770000, 27), #  iw -> Hebr
    (0xB2C80000, 40), #  iwm -> Latn
    (0xCAC80000, 40), #  iws -> Latn
    (0x9F280000, 40), #  izh -> Latn
    (0xA3280000, 40), #  izi -> Latn
    (0x6A610000, 31), #  ja -> Jpan
    (0x84090000, 40), #  jab -> Latn
    (0xB0090000, 40), #  jam -> Latn
    (0xD0290000, 40), #  jbu -> Latn
    (0xB4890000, 40), #  jen -> Latn
    (0xA8C90000, 40), #  jgk -> Latn
    (0xB8C90000, 40), #  jgo -> Latn
    (0x6A690000, 27), #  ji -> Hebr
    (0x85090000, 40), #  jib -> Latn
    (0x89890000, 40), #  jmc -> Latn
    (0xAD890000, 16), #  jml -> Deva
    (0x82290000, 40), #  jra -> Latn
    (0xCE890000, 40), #  jut -> Latn
    (0x6A760000, 40), #  jv -> Latn
    (0x6A770000, 40), #  jw -> Latn
    (0x6B610000, 19), #  ka -> Geor
    (0x800A0000, 15), #  kaa -> Cyrl
    (0x840A0000, 40), #  kab -> Latn
    (0x880A0000, 40), #  kac -> Latn
    (0x8C0A0000, 40), #  kad -> Latn
    (0xA00A0000, 40), #  kai -> Latn
    (0xA40A0000, 40), #  kaj -> Latn
    (0xB00A0000, 40), #  kam -> Latn
    (0xB80A0000, 40), #  kao -> Latn
    (0x8C2A0000, 15), #  kbd -> Cyrl
    (0xB02A0000, 40), #  kbm -> Latn
    (0xBC2A0000, 40), #  kbp -> Latn
    (0xC02A0000, 40), #  kbq -> Latn
    (0xDC2A0000, 40), #  kbx -> Latn
    (0xE02A0000,  1), #  kby -> Arab
    (0x984A0000, 40), #  kcg -> Latn
    (0xA84A0000, 40), #  kck -> Latn
    (0xAC4A0000, 40), #  kcl -> Latn
    (0xCC4A0000, 40), #  kct -> Latn
    (0x906A0000, 40), #  kde -> Latn
    (0x9C6A0000,  1), #  kdh -> Arab
    (0xAC6A0000, 40), #  kdl -> Latn
    (0xCC6A0000, 80), #  kdt -> Thai
    (0x808A0000, 40), #  kea -> Latn
    (0xB48A0000, 40), #  ken -> Latn
    (0xE48A0000, 40), #  kez -> Latn
    (0xB8AA0000, 40), #  kfo -> Latn
    (0xC4AA0000, 16), #  kfr -> Deva
    (0xE0AA0000, 16), #  kfy -> Deva
    (0x6B670000, 40), #  kg -> Latn
    (0x90CA0000, 40), #  kge -> Latn
    (0x94CA0000, 40), #  kgf -> Latn
    (0xBCCA0000, 40), #  kgp -> Latn
    (0x80EA0000, 40), #  kha -> Latn
    (0x84EA0000, 73), #  khb -> Talu
    (0xB4EA0000, 16), #  khn -> Deva
    (0xC0EA0000, 40), #  khq -> Latn
    (0xC8EA0000, 40), #  khs -> Latn
    (0xCCEA0000, 52), #  kht -> Mymr
    (0xD8EA0000,  1), #  khw -> Arab
    (0xE4EA0000, 40), #  khz -> Latn
    (0x6B690000, 40), #  ki -> Latn
    (0xA50A0000, 40), #  kij -> Latn
    (0xD10A0000, 40), #  kiu -> Latn
    (0xD90A0000, 40), #  kiw -> Latn
    (0x6B6A0000, 40), #  kj -> Latn
    (0x8D2A0000, 40), #  kjd -> Latn
    (0x992A0000, 39), #  kjg -> Laoo
    (0xC92A0000, 40), #  kjs -> Latn
    (0xE12A0000, 40), #  kjy -> Latn
    (0x6B6B0000, 15), #  kk -> Cyrl
    (0x6B6B4146,  1), #  kk-AF -> Arab
    (0x6B6B434E,  1), #  kk-CN -> Arab
    (0x6B6B4952,  1), #  kk-IR -> Arab
    (0x6B6B4D4E,  1), #  kk-MN -> Arab
    (0x894A0000, 40), #  kkc -> Latn
    (0xA54A0000, 40), #  kkj -> Latn
    (0x6B6C0000, 40), #  kl -> Latn
    (0xB56A0000, 40), #  kln -> Latn
    (0xC16A0000, 40), #  klq -> Latn
    (0xCD6A0000, 40), #  klt -> Latn
    (0xDD6A0000, 40), #  klx -> Latn
    (0x6B6D0000, 35), #  km -> Khmr
    (0x858A0000, 40), #  kmb -> Latn
    (0x9D8A0000, 40), #  kmh -> Latn
    (0xB98A0000, 40), #  kmo -> Latn
    (0xC98A0000, 40), #  kms -> Latn
    (0xD18A0000, 40), #  kmu -> Latn
    (0xD98A0000, 40), #  kmw -> Latn
    (0x6B6E0000, 36), #  kn -> Knda
    (0xBDAA0000, 40), #  knp -> Latn
    (0x6B6F0000, 37), #  ko -> Kore
    (0xA1CA0000, 15), #  koi -> Cyrl
    (0xA9CA0000, 16), #  kok -> Deva
    (0xADCA0000, 40), #  kol -> Latn
    (0xC9CA0000, 40), #  kos -> Latn
    (0xE5CA0000, 40), #  koz -> Latn
    (0x91EA0000, 40), #  kpe -> Latn
    (0x95EA0000, 40), #  kpf -> Latn
    (0xB9EA0000, 40), #  kpo -> Latn
    (0xC5EA0000, 40), #  kpr -> Latn
    (0xDDEA0000, 40), #  kpx -> Latn
    (0x860A0000, 40), #  kqb -> Latn
    (0x960A0000, 40), #  kqf -> Latn
    (0xCA0A0000, 40), #  kqs -> Latn
    (0xE20A0000, 18), #  kqy -> Ethi
    (0x8A2A0000, 15), #  krc -> Cyrl
    (0xA22A0000, 40), #  kri -> Latn
    (0xA62A0000, 40), #  krj -> Latn
    (0xAE2A0000, 40), #  krl -> Latn
    (0xCA2A0000, 40), #  krs -> Latn
    (0xD22A0000, 16), #  kru -> Deva
    (0x6B730000,  1), #  ks -> Arab
    (0x864A0000, 40), #  ksb -> Latn
    (0x8E4A0000, 40), #  ksd -> Latn
    (0x964A0000, 40), #  ksf -> Latn
    (0x9E4A0000, 40), #  ksh -> Latn
    (0xA64A0000, 40), #  ksj -> Latn
    (0xC64A0000, 40), #  ksr -> Latn
    (0x866A0000, 18), #  ktb -> Ethi
    (0xB26A0000, 40), #  ktm -> Latn
    (0xBA6A0000, 40), #  kto -> Latn
    (0x6B750000, 40), #  ku -> Latn
    (0x6B754952,  1), #  ku-IR -> Arab
    (0x6B754C42,  1), #  ku-LB -> Arab
    (0x868A0000, 40), #  kub -> Latn
    (0x8E8A0000, 40), #  kud -> Latn
    (0x928A0000, 40), #  kue -> Latn
    (0xA68A0000, 40), #  kuj -> Latn
    (0xB28A0000, 15), #  kum -> Cyrl
    (0xB68A0000, 40), #  kun -> Latn
    (0xBE8A0000, 40), #  kup -> Latn
    (0xCA8A0000, 40), #  kus -> Latn
    (0x6B760000, 15), #  kv -> Cyrl
    (0x9AAA0000, 40), #  kvg -> Latn
    (0xC6AA0000, 40), #  kvr -> Latn
    (0xDEAA0000,  1), #  kvx -> Arab
    (0x6B770000, 40), #  kw -> Latn
    (0xA6CA0000, 40), #  kwj -> Latn
    (0xBACA0000, 40), #  kwo -> Latn
    (0x82EA0000, 40), #  kxa -> Latn
    (0x8AEA0000, 18), #  kxc -> Ethi
    (0xB2EA0000, 80), #  kxm -> Thai
    (0xBEEA0000,  1), #  kxp -> Arab
    (0xDAEA0000, 40), #  kxw -> Latn
    (0xE6EA0000, 40), #  kxz -> Latn
    (0x6B790000, 15), #  ky -> Cyrl
    (0x6B79434E,  1), #  ky-CN -> Arab
    (0x6B795452, 40), #  ky-TR -> Latn
    (0x930A0000, 40), #  kye -> Latn
    (0xDF0A0000, 40), #  kyx -> Latn
    (0xC72A0000, 40), #  kzr -> Latn
    (0x6C610000, 40), #  la -> Latn
    (0x840B0000, 42), #  lab -> Lina
    (0x8C0B0000, 27), #  lad -> Hebr
    (0x980B0000, 40), #  lag -> Latn
    (0x9C0B0000,  1), #  lah -> Arab
    (0xA40B0000, 40), #  laj -> Latn
    (0xC80B0000, 40), #  las -> Latn
    (0x6C620000, 40), #  lb -> Latn
    (0x902B0000, 15), #  lbe -> Cyrl
    (0xD02B0000, 40), #  lbu -> Latn
    (0xD82B0000, 40), #  lbw -> Latn
    (0xB04B0000, 40), #  lcm -> Latn
    (0xBC4B0000, 80), #  lcp -> Thai
    (0x846B0000, 40), #  ldb -> Latn
    (0x8C8B0000, 40), #  led -> Latn
    (0x908B0000, 40), #  lee -> Latn
    (0xB08B0000, 40), #  lem -> Latn
    (0xBC8B0000, 41), #  lep -> Lepc
    (0xC08B0000, 40), #  leq -> Latn
    (0xD08B0000, 40), #  leu -> Latn
    (0xE48B0000, 15), #  lez -> Cyrl
    (0x6C670000, 40), #  lg -> Latn
    (0x98CB0000, 40), #  lgg -> Latn
    (0x6C690000, 40), #  li -> Latn
    (0x810B0000, 40), #  lia -> Latn
    (0x8D0B0000, 40), #  lid -> Latn
    (0x950B0000, 16), #  lif -> Deva
    (0x990B0000, 40), #  lig -> Latn
    (0x9D0B0000, 40), #  lih -> Latn
    (0xA50B0000, 40), #  lij -> Latn
    (0xC90B0000, 43), #  lis -> Lisu
    (0xBD2B0000, 40), #  ljp -> Latn
    (0xA14B0000,  1), #  lki -> Arab
    (0xCD4B0000, 40), #  lkt -> Latn
    (0x916B0000, 40), #  lle -> Latn
    (0xB56B0000, 40), #  lln -> Latn
    (0xB58B0000, 77), #  lmn -> Telu
    (0xB98B0000, 40), #  lmo -> Latn
    (0xBD8B0000, 40), #  lmp -> Latn
    (0x6C6E0000, 40), #  ln -> Latn
    (0xC9AB0000, 40), #  lns -> Latn
    (0xD1AB0000, 40), #  lnu -> Latn
    (0x6C6F0000, 39), #  lo -> Laoo
    (0xA5CB0000, 40), #  loj -> Latn
    (0xA9CB0000, 40), #  lok -> Latn
    (0xADCB0000, 40), #  lol -> Latn
    (0xC5CB0000, 40), #  lor -> Latn
    (0xC9CB0000, 40), #  los -> Latn
    (0xE5CB0000, 40), #  loz -> Latn
    (0x8A2B0000,  1), #  lrc -> Arab
    (0x6C740000, 40), #  lt -> Latn
    (0x9A6B0000, 40), #  ltg -> Latn
    (0x6C750000, 40), #  lu -> Latn
    (0x828B0000, 40), #  lua -> Latn
    (0xBA8B0000, 40), #  luo -> Latn
    (0xE28B0000, 40), #  luy -> Latn
    (0xE68B0000,  1), #  luz -> Arab
    (0x6C760000, 40), #  lv -> Latn
    (0xAECB0000, 80), #  lwl -> Thai
    (0x9F2B0000, 24), #  lzh -> Hans
    (0xE72B0000, 40), #  lzz -> Latn
    (0x8C0C0000, 40), #  mad -> Latn
    (0x940C0000, 40), #  maf -> Latn
    (0x980C0000, 16), #  mag -> Deva
    (0xA00C0000, 16), #  mai -> Deva
    (0xA80C0000, 40), #  mak -> Latn
    (0xB40C0000, 40), #  man -> Latn
    (0xB40C474E, 54), #  man-GN -> Nkoo
    (0xC80C0000, 40), #  mas -> Latn
    (0xD80C0000, 40), #  maw -> Latn
    (0xE40C0000, 40), #  maz -> Latn
    (0x9C2C0000, 40), #  mbh -> Latn
    (0xB82C0000, 40), #  mbo -> Latn
    (0xC02C0000, 40), #  mbq -> Latn
    (0xD02C0000, 40), #  mbu -> Latn
    (0xD82C0000, 40), #  mbw -> Latn
    (0xA04C0000, 40), #  mci -> Latn
    (0xBC4C0000, 40), #  mcp -> Latn
    (0xC04C0000, 40), #  mcq -> Latn
    (0xC44C0000, 40), #  mcr -> Latn
    (0xD04C0000, 40), #  mcu -> Latn
    (0x806C0000, 40), #  mda -> Latn
    (0x906C0000,  1), #  mde -> Arab
    (0x946C0000, 15), #  mdf -> Cyrl
    (0x9C6C0000, 40), #  mdh -> Latn
    (0xA46C0000, 40), #  mdj -> Latn
    (0xC46C0000, 40), #  mdr -> Latn
    (0xDC6C0000, 18), #  mdx -> Ethi
    (0x8C8C0000, 40), #  med -> Latn
    (0x908C0000, 40), #  mee -> Latn
    (0xA88C0000, 40), #  mek -> Latn
    (0xB48C0000, 40), #  men -> Latn
    (0xC48C0000, 40), #  mer -> Latn
    (0xCC8C0000, 40), #  met -> Latn
    (0xD08C0000, 40), #  meu -> Latn
    (0x80AC0000,  1), #  mfa -> Arab
    (0x90AC0000, 40), #  mfe -> Latn
    (0xB4AC0000, 40), #  mfn -> Latn
    (0xB8AC0000, 40), #  mfo -> Latn
    (0xC0AC0000, 40), #  mfq -> Latn
    (0x6D670000, 40), #  mg -> Latn
    (0x9CCC0000, 40), #  mgh -> Latn
    (0xACCC0000, 40), #  mgl -> Latn
    (0xB8CC0000, 40), #  mgo -> Latn
    (0xBCCC0000, 16), #  mgp -> Deva
    (0xE0CC0000, 40), #  mgy -> Latn
    (0x6D680000, 40), #  mh -> Latn
    (0xA0EC0000, 40), #  mhi -> Latn
    (0xACEC0000, 40), #  mhl -> Latn
    (0x6D690000, 40), #  mi -> Latn
    (0x950C0000, 40), #  mif -> Latn
    (0xB50C0000, 40), #  min -> Latn
    (0xC90C0000, 26), #  mis -> Hatr
    (0xD90C0000, 40), #  miw -> Latn
    (0x6D6B0000, 15), #  mk -> Cyrl
    (0xA14C0000,  1), #  mki -> Arab
    (0xAD4C0000, 40), #  mkl -> Latn
    (0xBD4C0000, 40), #  mkp -> Latn
    (0xD94C0000, 40), #  mkw -> Latn
    (0x6D6C0000, 49), #  ml -> Mlym
    (0x916C0000, 40), #  mle -> Latn
    (0xBD6C0000, 40), #  mlp -> Latn
    (0xC96C0000, 40), #  mls -> Latn
    (0xB98C0000, 40), #  mmo -> Latn
    (0xD18C0000, 40), #  mmu -> Latn
    (0xDD8C0000, 40), #  mmx -> Latn
    (0x6D6E0000, 15), #  mn -> Cyrl
    (0x6D6E434E, 50), #  mn-CN -> Mong
    (0x81AC0000, 40), #  mna -> Latn
    (0x95AC0000, 40), #  mnf -> Latn
    (0xA1AC0000,  7), #  mni -> Beng
    (0xD9AC0000, 52), #  mnw -> Mymr
    (0x81CC0000, 40), #  moa -> Latn
    (0x91CC0000, 40), #  moe -> Latn
    (0x9DCC0000, 40), #  moh -> Latn
    (0xC9CC0000, 40), #  mos -> Latn
    (0xDDCC0000, 40), #  mox -> Latn
    (0xBDEC0000, 40), #  mpp -> Latn
    (0xC9EC0000, 40), #  mps -> Latn
    (0xCDEC0000, 40), #  mpt -> Latn
    (0xDDEC0000, 40), #  mpx -> Latn
    (0xAE0C0000, 40), #  mql -> Latn
    (0x6D720000, 16), #  mr -> Deva
    (0x8E2C0000, 16), #  mrd -> Deva
    (0xA62C0000, 15), #  mrj -> Cyrl
    (0xBA2C0000, 51), #  mro -> Mroo
    (0x6D730000, 40), #  ms -> Latn
    (0x6D734343,  1), #  ms-CC -> Arab
    (0x6D734944,  1), #  ms-ID -> Arab
    (0x6D740000, 40), #  mt -> Latn
    (0x8A6C0000, 40), #  mtc -> Latn
    (0x966C0000, 40), #  mtf -> Latn
    (0xA26C0000, 40), #  mti -> Latn
    (0xC66C0000, 16), #  mtr -> Deva
    (0x828C0000, 40), #  mua -> Latn
    (0xC68C0000, 40), #  mur -> Latn
    (0xCA8C0000, 40), #  mus -> Latn
    (0x82AC0000, 40), #  mva -> Latn
    (0xB6AC0000, 40), #  mvn -> Latn
    (0xE2AC0000,  1), #  mvy -> Arab
    (0xAACC0000, 40), #  mwk -> Latn
    (0xC6CC0000, 16), #  mwr -> Deva
    (0xD6CC0000, 40), #  mwv -> Latn
    (0x8AEC0000, 40), #  mxc -> Latn
    (0xB2EC0000, 40), #  mxm -> Latn
    (0x6D790000, 52), #  my -> Mymr
    (0xAB0C0000, 40), #  myk -> Latn
    (0xB30C0000, 18), #  mym -> Ethi
    (0xD70C0000, 15), #  myv -> Cyrl
    (0xDB0C0000, 40), #  myw -> Latn
    (0xDF0C0000, 40), #  myx -> Latn
    (0xE70C0000, 46), #  myz -> Mand
    (0xAB2C0000, 40), #  mzk -> Latn
    (0xB32C0000, 40), #  mzm -> Latn
    (0xB72C0000,  1), #  mzn -> Arab
    (0xBF2C0000, 40), #  mzp -> Latn
    (0xDB2C0000, 40), #  mzw -> Latn
    (0xE72C0000, 40), #  mzz -> Latn
    (0x6E610000, 40), #  na -> Latn
    (0x880D0000, 40), #  nac -> Latn
    (0x940D0000, 40), #  naf -> Latn
    (0xA80D0000, 40), #  nak -> Latn
    (0xB40D0000, 24), #  nan -> Hans
    (0xBC0D0000, 40), #  nap -> Latn
    (0xC00D0000, 40), #  naq -> Latn
    (0xC80D0000, 40), #  nas -> Latn
    (0x6E620000, 40), #  nb -> Latn
    (0x804D0000, 40), #  nca -> Latn
    (0x904D0000, 40), #  nce -> Latn
    (0x944D0000, 40), #  ncf -> Latn
    (0x9C4D0000, 40), #  nch -> Latn
    (0xB84D0000, 40), #  nco -> Latn
    (0xD04D0000, 40), #  ncu -> Latn
    (0x6E640000, 40), #  nd -> Latn
    (0x886D0000, 40), #  ndc -> Latn
    (0xC86D0000, 40), #  nds -> Latn
    (0x6E650000, 16), #  ne -> Deva
    (0x848D0000, 40), #  neb -> Latn
    (0xD88D0000, 16), #  new -> Deva
    (0xDC8D0000, 40), #  nex -> Latn
    (0xC4AD0000, 40), #  nfr -> Latn
    (0x6E670000, 40), #  ng -> Latn
    (0x80CD0000, 40), #  nga -> Latn
    (0x84CD0000, 40), #  ngb -> Latn
    (0xACCD0000, 40), #  ngl -> Latn
    (0x84ED0000, 40), #  nhb -> Latn
    (0x90ED0000, 40), #  nhe -> Latn
    (0xD8ED0000, 40), #  nhw -> Latn
    (0x950D0000, 40), #  nif -> Latn
    (0xA10D0000, 40), #  nii -> Latn
    (0xA50D0000, 40), #  nij -> Latn
    (0xB50D0000, 40), #  nin -> Latn
    (0xD10D0000, 40), #  niu -> Latn
    (0xE10D0000, 40), #  niy -> Latn
    (0xE50D0000, 40), #  niz -> Latn
    (0xB92D0000, 40), #  njo -> Latn
    (0x994D0000, 40), #  nkg -> Latn
    (0xB94D0000, 40), #  nko -> Latn
    (0x6E6C0000, 40), #  nl -> Latn
    (0x998D0000, 40), #  nmg -> Latn
    (0xE58D0000, 40), #  nmz -> Latn
    (0x6E6E0000, 40), #  nn -> Latn
    (0x95AD0000, 40), #  nnf -> Latn
    (0x9DAD0000, 40), #  nnh -> Latn
    (0xA9AD0000, 40), #  nnk -> Latn
    (0xB1AD0000, 40), #  nnm -> Latn
    (0x6E6F0000, 40), #  no -> Latn
    (0x8DCD0000, 38), #  nod -> Lana
    (0x91CD0000, 16), #  noe -> Deva
    (0xB5CD0000, 64), #  non -> Runr
    (0xBDCD0000, 40), #  nop -> Latn
    (0xD1CD0000, 40), #  nou -> Latn
    (0xBA0D0000, 54), #  nqo -> Nkoo
    (0x6E720000, 40), #  nr -> Latn
    (0x862D0000, 40), #  nrb -> Latn
    (0xAA4D0000,  9), #  nsk -> Cans
    (0xB64D0000, 40), #  nsn -> Latn
    (0xBA4D0000, 40), #  nso -> Latn
    (0xCA4D0000, 40), #  nss -> Latn
    (0xB26D0000, 40), #  ntm -> Latn
    (0xC66D0000, 40), #  ntr -> Latn
    (0xA28D0000, 40), #  nui -> Latn
    (0xBE8D0000, 40), #  nup -> Latn
    (0xCA8D0000, 40), #  nus -> Latn
    (0xD68D0000, 40), #  nuv -> Latn
    (0xDE8D0000, 40), #  nux -> Latn
    (0x6E760000, 40), #  nv -> Latn
    (0x86CD0000, 40), #  nwb -> Latn
    (0xC2ED0000, 40), #  nxq -> Latn
    (0xC6ED0000, 40), #  nxr -> Latn
    (0x6E790000, 40), #  ny -> Latn
    (0xB30D0000, 40), #  nym -> Latn
    (0xB70D0000, 40), #  nyn -> Latn
    (0xA32D0000, 40), #  nzi -> Latn
    (0x6F630000, 40), #  oc -> Latn
    (0x88CE0000, 40), #  ogc -> Latn
    (0xC54E0000, 40), #  okr -> Latn
    (0xD54E0000, 40), #  okv -> Latn
    (0x6F6D0000, 40), #  om -> Latn
    (0x99AE0000, 40), #  ong -> Latn
    (0xB5AE0000, 40), #  onn -> Latn
    (0xC9AE0000, 40), #  ons -> Latn
    (0xB1EE0000, 40), #  opm -> Latn
    (0x6F720000, 57), #  or -> Orya
    (0xBA2E0000, 40), #  oro -> Latn
    (0xD22E0000,  1), #  oru -> Arab
    (0x6F730000, 15), #  os -> Cyrl
    (0x824E0000, 58), #  osa -> Osge
    (0x826E0000,  1), #  ota -> Arab
    (0xAA6E0000, 56), #  otk -> Orkh
    (0xB32E0000, 40), #  ozm -> Latn
    (0x70610000, 23), #  pa -> Guru
    (0x7061504B,  1), #  pa-PK -> Arab
    (0x980F0000, 40), #  pag -> Latn
    (0xAC0F0000, 60), #  pal -> Phli
    (0xB00F0000, 40), #  pam -> Latn
    (0xBC0F0000, 40), #  pap -> Latn
    (0xD00F0000, 40), #  pau -> Latn
    (0xA02F0000, 40), #  pbi -> Latn
    (0x8C4F0000, 40), #  pcd -> Latn
    (0xB04F0000, 40), #  pcm -> Latn
    (0x886F0000, 40), #  pdc -> Latn
    (0xCC6F0000, 40), #  pdt -> Latn
    (0x8C8F0000, 40), #  ped -> Latn
    (0xB88F0000, 84), #  peo -> Xpeo
    (0xDC8F0000, 40), #  pex -> Latn
    (0xACAF0000, 40), #  pfl -> Latn
    (0xACEF0000,  1), #  phl -> Arab
    (0xB4EF0000, 61), #  phn -> Phnx
    (0xAD0F0000, 40), #  pil -> Latn
    (0xBD0F0000, 40), #  pip -> Latn
    (0x814F0000,  8), #  pka -> Brah
    (0xB94F0000, 40), #  pko -> Latn
    (0x706C0000, 40), #  pl -> Latn
    (0x816F0000, 40), #  pla -> Latn
    (0xC98F0000, 40), #  pms -> Latn
    (0x99AF0000, 40), #  png -> Latn
    (0xB5AF0000, 40), #  pnn -> Latn
    (0xCDAF0000, 21), #  pnt -> Grek
    (0xB5CF0000, 40), #  pon -> Latn
    (0xB9EF0000, 40), #  ppo -> Latn
    (0x822F0000, 34), #  pra -> Khar
    (0x8E2F0000,  1), #  prd -> Arab
    (0x9A2F0000, 40), #  prg -> Latn
    (0x70730000,  1), #  ps -> Arab
    (0xCA4F0000, 40), #  pss -> Latn
    (0x70740000, 40), #  pt -> Latn
    (0xBE6F0000, 40), #  ptp -> Latn
    (0xD28F0000, 40), #  puu -> Latn
    (0x82CF0000, 40), #  pwa -> Latn
    (0x71750000, 40), #  qu -> Latn
    (0x8A900000, 40), #  quc -> Latn
    (0x9A900000, 40), #  qug -> Latn
    (0xA0110000, 40), #  rai -> Latn
    (0xA4110000, 16), #  raj -> Deva
    (0xB8110000, 40), #  rao -> Latn
    (0x94510000, 40), #  rcf -> Latn
    (0xA4910000, 40), #  rej -> Latn
    (0xAC910000, 40), #  rel -> Latn
    (0xC8910000, 40), #  res -> Latn
    (0xB4D10000, 40), #  rgn -> Latn
    (0x98F10000,  1), #  rhg -> Arab
    (0x81110000, 40), #  ria -> Latn
    (0x95110000, 78), #  rif -> Tfng
    (0x95114E4C, 40), #  rif-NL -> Latn
    (0xC9310000, 16), #  rjs -> Deva
    (0xCD510000,  7), #  rkt -> Beng
    (0x726D0000, 40), #  rm -> Latn
    (0x95910000, 40), #  rmf -> Latn
    (0xB9910000, 40), #  rmo -> Latn
    (0xCD910000,  1), #  rmt -> Arab
    (0xD1910000, 40), #  rmu -> Latn
    (0x726E0000, 40), #  rn -> Latn
    (0x81B10000, 40), #  rna -> Latn
    (0x99B10000, 40), #  rng -> Latn
    (0x726F0000, 40), #  ro -> Latn
    (0x85D10000, 40), #  rob -> Latn
    (0x95D10000, 40), #  rof -> Latn
    (0xB9D10000, 40), #  roo -> Latn
    (0xBA310000, 40), #  rro -> Latn
    (0xB2710000, 40), #  rtm -> Latn
    (0x72750000, 15), #  ru -> Cyrl
    (0x92910000, 15), #  rue -> Cyrl
    (0x9A910000, 40), #  rug -> Latn
    (0x72770000, 40), #  rw -> Latn
    (0xAAD10000, 40), #  rwk -> Latn
    (0xBAD10000, 40), #  rwo -> Latn
    (0xD3110000, 33), #  ryu -> Kana
    (0x73610000, 16), #  sa -> Deva
    (0x94120000, 40), #  saf -> Latn
    (0x9C120000, 15), #  sah -> Cyrl
    (0xC0120000, 40), #  saq -> Latn
    (0xC8120000, 40), #  sas -> Latn
    (0xCC120000, 40), #  sat -> Latn
    (0xE4120000, 67), #  saz -> Saur
    (0x80320000, 40), #  sba -> Latn
    (0x90320000, 40), #  sbe -> Latn
    (0xBC320000, 40), #  sbp -> Latn
    (0x73630000, 40), #  sc -> Latn
    (0xA8520000, 16), #  sck -> Deva
    (0xAC520000,  1), #  scl -> Arab
    (0xB4520000, 40), #  scn -> Latn
    (0xB8520000, 40), #  sco -> Latn
    (0xC8520000, 40), #  scs -> Latn
    (0x73640000,  1), #  sd -> Arab
    (0x88720000, 40), #  sdc -> Latn
    (0x9C720000,  1), #  sdh -> Arab
    (0x73650000, 40), #  se -> Latn
    (0x94920000, 40), #  sef -> Latn
    (0x9C920000, 40), #  seh -> Latn
    (0xA0920000, 40), #  sei -> Latn
    (0xC8920000, 40), #  ses -> Latn
    (0x73670000, 40), #  sg -> Latn
    (0x80D20000, 55), #  sga -> Ogam
    (0xC8D20000, 40), #  sgs -> Latn
    (0xD8D20000, 18), #  sgw -> Ethi
    (0xE4D20000, 40), #  sgz -> Latn
    (0x73680000, 40), #  sh -> Latn
    (0xA0F20000, 78), #  shi -> Tfng
    (0xA8F20000, 40), #  shk -> Latn
    (0xB4F20000, 52), #  shn -> Mymr
    (0xD0F20000,  1), #  shu -> Arab
    (0x73690000, 69), #  si -> Sinh
    (0x8D120000, 40), #  sid -> Latn
    (0x99120000, 40), #  sig -> Latn
    (0xAD120000, 40), #  sil -> Latn
    (0xB1120000, 40), #  sim -> Latn
    (0xC5320000, 40), #  sjr -> Latn
    (0x736B0000, 40), #  sk -> Latn
    (0x89520000, 40), #  skc -> Latn
    (0xC5520000,  1), #  skr -> Arab
    (0xC9520000, 40), #  sks -> Latn
    (0x736C0000, 40), #  sl -> Latn
    (0x8D720000, 40), #  sld -> Latn
    (0xA1720000, 40), #  sli -> Latn
    (0xAD720000, 40), #  sll -> Latn
    (0xE1720000, 40), #  sly -> Latn
    (0x736D0000, 40), #  sm -> Latn
    (0x81920000, 40), #  sma -> Latn
    (0xA5920000, 40), #  smj -> Latn
    (0xB5920000, 40), #  smn -> Latn
    (0xBD920000, 65), #  smp -> Samr
    (0xC1920000, 40), #  smq -> Latn
    (0xC9920000, 40), #  sms -> Latn
    (0x736E0000, 40), #  sn -> Latn
    (0x89B20000, 40), #  snc -> Latn
    (0xA9B20000, 40), #  snk -> Latn
    (0xBDB20000, 40), #  snp -> Latn
    (0xDDB20000, 40), #  snx -> Latn
    (0xE1B20000, 40), #  sny -> Latn
    (0x736F0000, 40), #  so -> Latn
    (0xA9D20000, 40), #  sok -> Latn
    (0xC1D20000, 40), #  soq -> Latn
    (0xD1D20000, 80), #  sou -> Thai
    (0xE1D20000, 40), #  soy -> Latn
    (0x8DF20000, 40), #  spd -> Latn
    (0xADF20000, 40), #  spl -> Latn
    (0xC9F20000, 40), #  sps -> Latn
    (0x73710000, 40), #  sq -> Latn
    (0x73720000, 15), #  sr -> Cyrl
    (0x73724D45, 40), #  sr-ME -> Latn
    (0x7372524F, 40), #  sr-RO -> Latn
    (0x73725255, 40), #  sr-RU -> Latn
    (0x73725452, 40), #  sr-TR -> Latn
    (0x86320000, 70), #  srb -> Sora
    (0xB6320000, 40), #  srn -> Latn
    (0xC6320000, 40), #  srr -> Latn
    (0xDE320000, 16), #  srx -> Deva
    (0x73730000, 40), #  ss -> Latn
    (0x8E520000, 40), #  ssd -> Latn
    (0x9A520000, 40), #  ssg -> Latn
    (0xE2520000, 40), #  ssy -> Latn
    (0x73740000, 40), #  st -> Latn
    (0xAA720000, 40), #  stk -> Latn
    (0xC2720000, 40), #  stq -> Latn
    (0x73750000, 40), #  su -> Latn
    (0x82920000, 40), #  sua -> Latn
    (0x92920000, 40), #  sue -> Latn
    (0xAA920000, 40), #  suk -> Latn
    (0xC6920000, 40), #  sur -> Latn
    (0xCA920000, 40), #  sus -> Latn
    (0x73760000, 40), #  sv -> Latn
    (0x73770000, 40), #  sw -> Latn
    (0x86D20000,  1), #  swb -> Arab
    (0x8AD20000, 40), #  swc -> Latn
    (0x9AD20000, 40), #  swg -> Latn
    (0xBED20000, 40), #  swp -> Latn
    (0xD6D20000, 16), #  swv -> Deva
    (0xB6F20000, 40), #  sxn -> Latn
    (0xDAF20000, 40), #  sxw -> Latn
    (0xAF120000,  7), #  syl -> Beng
    (0xC7120000, 71), #  syr -> Syrc
    (0xAF320000, 40), #  szl -> Latn
    (0x74610000, 74), #  ta -> Taml
    (0xA4130000, 16), #  taj -> Deva
    (0xAC130000, 40), #  tal -> Latn
    (0xB4130000, 40), #  tan -> Latn
    (0xC0130000, 40), #  taq -> Latn
    (0x88330000, 40), #  tbc -> Latn
    (0x8C330000, 40), #  tbd -> Latn
    (0x94330000, 40), #  tbf -> Latn
    (0x98330000, 40), #  tbg -> Latn
    (0xB8330000, 40), #  tbo -> Latn
    (0xD8330000, 40), #  tbw -> Latn
    (0xE4330000, 40), #  tbz -> Latn
    (0xA0530000, 40), #  tci -> Latn
    (0xE0530000, 36), #  tcy -> Knda
    (0x8C730000, 72), #  tdd -> Tale
    (0x98730000, 16), #  tdg -> Deva
    (0x9C730000, 16), #  tdh -> Deva
    (0x74650000, 77), #  te -> Telu
    (0x8C930000, 40), #  ted -> Latn
    (0xB0930000, 40), #  tem -> Latn
    (0xB8930000, 40), #  teo -> Latn
    (0xCC930000, 40), #  tet -> Latn
    (0xA0B30000, 40), #  tfi -> Latn
    (0x74670000, 15), #  tg -> Cyrl
    (0x7467504B,  1), #  tg-PK -> Arab
    (0x88D30000, 40), #  tgc -> Latn
    (0xB8D30000, 40), #  tgo -> Latn
    (0xD0D30000, 40), #  tgu -> Latn
    (0x74680000, 80), #  th -> Thai
    (0xACF30000, 16), #  thl -> Deva
    (0xC0F30000, 16), #  thq -> Deva
    (0xC4F30000, 16), #  thr -> Deva
    (0x74690000, 18), #  ti -> Ethi
    (0x95130000, 40), #  tif -> Latn
    (0x99130000, 18), #  tig -> Ethi
    (0xA9130000, 40), #  tik -> Latn
    (0xB1130000, 40), #  tim -> Latn
    (0xB9130000, 40), #  tio -> Latn
    (0xD5130000, 40), #  tiv -> Latn
    (0x746B0000, 40), #  tk -> Latn
    (0xAD530000, 40), #  tkl -> Latn
    (0xC5530000, 40), #  tkr -> Latn
    (0xCD530000, 16), #  tkt -> Deva
    (0x746C0000, 40), #  tl -> Latn
    (0x95730000, 40), #  tlf -> Latn
    (0xDD730000, 40), #  tlx -> Latn
    (0xE1730000, 40), #  tly -> Latn
    (0x9D930000, 40), #  tmh -> Latn
    (0xE1930000, 40), #  tmy -> Latn
    (0x746E0000, 40), #  tn -> Latn
    (0x9DB30000, 40), #  tnh -> Latn
    (0x746F0000, 40), #  to -> Latn
    (0x95D30000, 40), #  tof -> Latn
    (0x99D30000, 40), #  tog -> Latn
    (0xC1D30000, 40), #  toq -> Latn
    (0xA1F30000, 40), #  tpi -> Latn
    (0xB1F30000, 40), #  tpm -> Latn
    (0xE5F30000, 40), #  tpz -> Latn
    (0xBA130000, 40), #  tqo -> Latn
    (0x74720000, 40), #  tr -> Latn
    (0xD2330000, 40), #  tru -> Latn
    (0xD6330000, 40), #  trv -> Latn
    (0xDA330000,  1), #  trw -> Arab
    (0x74730000, 40), #  ts -> Latn
    (0x8E530000, 21), #  tsd -> Grek
    (0x96530000, 16), #  tsf -> Deva
    (0x9A530000, 40), #  tsg -> Latn
    (0xA6530000, 81), #  tsj -> Tibt
    (0xDA530000, 40), #  tsw -> Latn
    (0x74740000, 15), #  tt -> Cyrl
    (0x8E730000, 40), #  ttd -> Latn
    (0x92730000, 40), #  tte -> Latn
    (0xA6730000, 40), #  ttj -> Latn
    (0xC6730000, 40), #  ttr -> Latn
    (0xCA730000, 80), #  tts -> Thai
    (0xCE730000, 40), #  ttt -> Latn
    (0x9E930000, 40), #  tuh -> Latn
    (0xAE930000, 40), #  tul -> Latn
    (0xB2930000, 40), #  tum -> Latn
    (0xC2930000, 40), #  tuq -> Latn
    (0x8EB30000, 40), #  tvd -> Latn
    (0xAEB30000, 40), #  tvl -> Latn
    (0xD2B30000, 40), #  tvu -> Latn
    (0x9ED30000, 40), #  twh -> Latn
    (0xC2D30000, 40), #  twq -> Latn
    (0x9AF30000, 75), #  txg -> Tang
    (0x74790000, 40), #  ty -> Latn
    (0x83130000, 40), #  tya -> Latn
    (0xD7130000, 15), #  tyv -> Cyrl
    (0xB3330000, 40), #  tzm -> Latn
    (0xD0340000, 40), #  ubu -> Latn
    (0xB0740000, 15), #  udm -> Cyrl
    (0x75670000,  1), #  ug -> Arab
    (0x75674B5A, 15), #  ug-KZ -> Cyrl
    (0x75674D4E, 15), #  ug-MN -> Cyrl
    (0x80D40000, 82), #  uga -> Ugar
    (0x756B0000, 15), #  uk -> Cyrl
    (0xA1740000, 40), #  uli -> Latn
    (0x85940000, 40), #  umb -> Latn
    (0xC5B40000,  7), #  unr -> Beng
    (0xC5B44E50, 16), #  unr-NP -> Deva
    (0xDDB40000,  7), #  unx -> Beng
    (0x75720000,  1), #  ur -> Arab
    (0xA2340000, 40), #  uri -> Latn
    (0xCE340000, 40), #  urt -> Latn
    (0xDA340000, 40), #  urw -> Latn
    (0x82540000, 40), #  usa -> Latn
    (0xC6740000, 40), #  utr -> Latn
    (0x9EB40000, 40), #  uvh -> Latn
    (0xAEB40000, 40), #  uvl -> Latn
    (0x757A0000, 40), #  uz -> Latn
    (0x757A4146,  1), #  uz-AF -> Arab
    (0x757A434E, 15), #  uz-CN -> Cyrl
    (0x98150000, 40), #  vag -> Latn
    (0xA0150000, 83), #  vai -> Vaii
    (0xB4150000, 40), #  van -> Latn
    (0x76650000, 40), #  ve -> Latn
    (0x88950000, 40), #  vec -> Latn
    (0xBC950000, 40), #  vep -> Latn
    (0x76690000, 40), #  vi -> Latn
    (0x89150000, 40), #  vic -> Latn
    (0xD5150000, 40), #  viv -> Latn
    (0xC9750000, 40), #  vls -> Latn
    (0x95950000, 40), #  vmf -> Latn
    (0xD9950000, 40), #  vmw -> Latn
    (0x766F0000, 40), #  vo -> Latn
    (0xCDD50000, 40), #  vot -> Latn
    (0xBA350000, 40), #  vro -> Latn
    (0xB6950000, 40), #  vun -> Latn
    (0xCE950000, 40), #  vut -> Latn
    (0x77610000, 40), #  wa -> Latn
    (0x90160000, 40), #  wae -> Latn
    (0xA4160000, 40), #  waj -> Latn
    (0xAC160000, 18), #  wal -> Ethi
    (0xB4160000, 40), #  wan -> Latn
    (0xC4160000, 40), #  war -> Latn
    (0xBC360000, 40), #  wbp -> Latn
    (0xC0360000, 77), #  wbq -> Telu
    (0xC4360000, 16), #  wbr -> Deva
    (0xA0560000, 40), #  wci -> Latn
    (0xC4960000, 40), #  wer -> Latn
    (0xA0D60000, 40), #  wgi -> Latn
    (0x98F60000, 40), #  whg -> Latn
    (0x85160000, 40), #  wib -> Latn
    (0xD1160000, 40), #  wiu -> Latn
    (0xD5160000, 40), #  wiv -> Latn
    (0x81360000, 40), #  wja -> Latn
    (0xA1360000, 40), #  wji -> Latn
    (0xC9760000, 40), #  wls -> Latn
    (0xB9960000, 40), #  wmo -> Latn
    (0x89B60000, 40), #  wnc -> Latn
    (0xA1B60000,  1), #  wni -> Arab
    (0xD1B60000, 40), #  wnu -> Latn
    (0x776F0000, 40), #  wo -> Latn
    (0x85D60000, 40), #  wob -> Latn
    (0xC9D60000, 40), #  wos -> Latn
    (0xCA360000, 40), #  wrs -> Latn
    (0xAA560000, 40), #  wsk -> Latn
    (0xB2760000, 16), #  wtm -> Deva
    (0xD2960000, 24), #  wuu -> Hans
    (0xD6960000, 40), #  wuv -> Latn
    (0x82D60000, 40), #  wwa -> Latn
    (0xD4170000, 40), #  xav -> Latn
    (0xA0370000, 40), #  xbi -> Latn
    (0xC4570000, 10), #  xcr -> Cari
    (0xC8970000, 40), #  xes -> Latn
    (0x78680000, 40), #  xh -> Latn
    (0x81770000, 40), #  xla -> Latn
    (0x89770000, 44), #  xlc -> Lyci
    (0x8D770000, 45), #  xld -> Lydi
    (0x95970000, 19), #  xmf -> Geor
    (0xB5970000, 47), #  xmn -> Mani
    (0xC5970000, 48), #  xmr -> Merc
    (0x81B70000, 53), #  xna -> Narb
    (0xC5B70000, 16), #  xnr -> Deva
    (0x99D70000, 40), #  xog -> Latn
    (0xB5D70000, 40), #  xon -> Latn
    (0xC5F70000, 63), #  xpr -> Prti
    (0x86370000, 40), #  xrb -> Latn
    (0x82570000, 66), #  xsa -> Sarb
    (0xA2570000, 40), #  xsi -> Latn
    (0xB2570000, 40), #  xsm -> Latn
    (0xC6570000, 16), #  xsr -> Deva
    (0x92D70000, 40), #  xwe -> Latn
    (0xB0180000, 40), #  yam -> Latn
    (0xB8180000, 40), #  yao -> Latn
    (0xBC180000, 40), #  yap -> Latn
    (0xC8180000, 40), #  yas -> Latn
    (0xCC180000, 40), #  yat -> Latn
    (0xD4180000, 40), #  yav -> Latn
    (0xE0180000, 40), #  yay -> Latn
    (0xE4180000, 40), #  yaz -> Latn
    (0x80380000, 40), #  yba -> Latn
    (0x84380000, 40), #  ybb -> Latn
    (0xE0380000, 40), #  yby -> Latn
    (0xC4980000, 40), #  yer -> Latn
    (0xC4D80000, 40), #  ygr -> Latn
    (0xD8D80000, 40), #  ygw -> Latn
    (0x79690000, 27), #  yi -> Hebr
    (0xB9580000, 40), #  yko -> Latn
    (0x91780000, 40), #  yle -> Latn
    (0x99780000, 40), #  ylg -> Latn
    (0xAD780000, 40), #  yll -> Latn
    (0xAD980000, 40), #  yml -> Latn
    (0x796F0000, 40), #  yo -> Latn
    (0xB5D80000, 40), #  yon -> Latn
    (0x86380000, 40), #  yrb -> Latn
    (0x92380000, 40), #  yre -> Latn
    (0xAE380000, 40), #  yrl -> Latn
    (0xCA580000, 40), #  yss -> Latn
    (0x82980000, 40), #  yua -> Latn
    (0x92980000, 25), #  yue -> Hant
    (0x9298434E, 24), #  yue-CN -> Hans
    (0xA6980000, 40), #  yuj -> Latn
    (0xCE980000, 40), #  yut -> Latn
    (0xDA980000, 40), #  yuw -> Latn
    (0x7A610000, 40), #  za -> Latn
    (0x98190000, 40), #  zag -> Latn
    (0xA4790000,  1), #  zdj -> Arab
    (0x80990000, 40), #  zea -> Latn
    (0x9CD90000, 78), #  zgh -> Tfng
    (0x7A680000, 24), #  zh -> Hans
    (0x7A684155, 25), #  zh-AU -> Hant
    (0x7A68424E, 25), #  zh-BN -> Hant
    (0x7A684742, 25), #  zh-GB -> Hant
    (0x7A684746, 25), #  zh-GF -> Hant
    (0x7A68484B, 25), #  zh-HK -> Hant
    (0x7A684944, 25), #  zh-ID -> Hant
    (0x7A684D4F, 25), #  zh-MO -> Hant
    (0x7A684D59, 25), #  zh-MY -> Hant
    (0x7A685041, 25), #  zh-PA -> Hant
    (0x7A685046, 25), #  zh-PF -> Hant
    (0x7A685048, 25), #  zh-PH -> Hant
    (0x7A685352, 25), #  zh-SR -> Hant
    (0x7A685448, 25), #  zh-TH -> Hant
    (0x7A685457, 25), #  zh-TW -> Hant
    (0x7A685553, 25), #  zh-US -> Hant
    (0x7A68564E, 25), #  zh-VN -> Hant
    (0x81190000, 40), #  zia -> Latn
    (0xB1790000, 40), #  zlm -> Latn
    (0xA1990000, 40), #  zmi -> Latn
    (0x91B90000, 40), #  zne -> Latn
    (0x7A750000, 40), #  zu -> Latn
    (0x83390000, 40), #  zza -> Latn
])

REPRESENTATIVE_LOCALES = [
    0x616145544C61746E, #  aa_Latn_ET
    0x616247454379726C, #  ab_Cyrl_GE
    0xC42047484C61746E, #  abr_Latn_GH
    0x904049444C61746E, #  ace_Latn_ID
    0x9C4055474C61746E, #  ach_Latn_UG
    0x806047484C61746E, #  ada_Latn_GH
    0xE06052554379726C, #  ady_Cyrl_RU
    0x6165495241767374, #  ae_Avst_IR
    0x8480544E41726162, #  aeb_Arab_TN
    0x61665A414C61746E, #  af_Latn_ZA
    0xC0C0434D4C61746E, #  agq_Latn_CM
    0xB8E0494E41686F6D, #  aho_Ahom_IN
    0x616B47484C61746E, #  ak_Latn_GH
    0xA940495158737578, #  akk_Xsux_IQ
    0xB560584B4C61746E, #  aln_Latn_XK
    0xCD6052554379726C, #  alt_Cyrl_RU
    0x616D455445746869, #  am_Ethi_ET
    0xB9804E474C61746E, #  amo_Latn_NG
    0xE5C049444C61746E, #  aoz_Latn_ID
    0x8DE0544741726162, #  apd_Arab_TG
    0x6172454741726162, #  ar_Arab_EG
    0x8A20495241726D69, #  arc_Armi_IR
    0x8A204A4F4E626174, #  arc_Nbat_JO
    0x8A20535950616C6D, #  arc_Palm_SY
    0xB620434C4C61746E, #  arn_Latn_CL
    0xBA20424F4C61746E, #  aro_Latn_BO
    0xC220445A41726162, #  arq_Arab_DZ
    0xE2204D4141726162, #  ary_Arab_MA
    0xE620454741726162, #  arz_Arab_EG
    0x6173494E42656E67, #  as_Beng_IN
    0x8240545A4C61746E, #  asa_Latn_TZ
    0x9240555353676E77, #  ase_Sgnw_US
    0xCE4045534C61746E, #  ast_Latn_ES
    0xA66043414C61746E, #  atj_Latn_CA
    0x617652554379726C, #  av_Cyrl_RU
    0x82C0494E44657661, #  awa_Deva_IN
    0x6179424F4C61746E, #  ay_Latn_BO
    0x617A495241726162, #  az_Arab_IR
    0x617A415A4C61746E, #  az_Latn_AZ
    0x626152554379726C, #  ba_Cyrl_RU
    0xAC01504B41726162, #  bal_Arab_PK
    0xB40149444C61746E, #  ban_Latn_ID
    0xBC014E5044657661, #  bap_Deva_NP
    0xC40141544C61746E, #  bar_Latn_AT
    0xC801434D4C61746E, #  bas_Latn_CM
    0xDC01434D42616D75, #  bax_Bamu_CM
    0x882149444C61746E, #  bbc_Latn_ID
    0xA421434D4C61746E, #  bbj_Latn_CM
    0xA04143494C61746E, #  bci_Latn_CI
    0x626542594379726C, #  be_Cyrl_BY
    0xA481534441726162, #  bej_Arab_SD
    0xB0815A4D4C61746E, #  bem_Latn_ZM
    0xD88149444C61746E, #  bew_Latn_ID
    0xE481545A4C61746E, #  bez_Latn_TZ
    0x8CA1434D4C61746E, #  bfd_Latn_CM
    0xC0A1494E54616D6C, #  bfq_Taml_IN
    0xCCA1504B41726162, #  bft_Arab_PK
    0xE0A1494E44657661, #  bfy_Deva_IN
    0x626742474379726C, #  bg_Cyrl_BG
    0x88C1494E44657661, #  bgc_Deva_IN
    0xB4C1504B41726162, #  bgn_Arab_PK
    0xDCC154524772656B, #  bgx_Grek_TR
    0x84E1494E44657661, #  bhb_Deva_IN
    0xA0E1494E44657661, #  bhi_Deva_IN
    0xA8E150484C61746E, #  bhk_Latn_PH
    0xB8E1494E44657661, #  bho_Deva_IN
    0x626956554C61746E, #  bi_Latn_VU
    0xA90150484C61746E, #  bik_Latn_PH
    0xB5014E474C61746E, #  bin_Latn_NG
    0xA521494E44657661, #  bjj_Deva_IN
    0xB52149444C61746E, #  bjn_Latn_ID
    0xB141434D4C61746E, #  bkm_Latn_CM
    0xD14150484C61746E, #  bku_Latn_PH
    0xCD61564E54617674, #  blt_Tavt_VN
    0x626D4D4C4C61746E, #  bm_Latn_ML
    0xC1814D4C4C61746E, #  bmq_Latn_ML
    0x626E424442656E67, #  bn_Beng_BD
    0x626F434E54696274, #  bo_Tibt_CN
    0xE1E1494E42656E67, #  bpy_Beng_IN
    0xA201495241726162, #  bqi_Arab_IR
    0xD60143494C61746E, #  bqv_Latn_CI
    0x627246524C61746E, #  br_Latn_FR
    0x8221494E44657661, #  bra_Deva_IN
    0x9E21504B41726162, #  brh_Arab_PK
    0xDE21494E44657661, #  brx_Deva_IN
    0x627342414C61746E, #  bs_Latn_BA
    0xC2414C5242617373, #  bsq_Bass_LR
    0xCA41434D4C61746E, #  bss_Latn_CM
    0xBA6150484C61746E, #  bto_Latn_PH
    0xD661504B44657661, #  btv_Deva_PK
    0x828152554379726C, #  bua_Cyrl_RU
    0x8A8159544C61746E, #  buc_Latn_YT
    0x9A8149444C61746E, #  bug_Latn_ID
    0xB281434D4C61746E, #  bum_Latn_CM
    0x86A147514C61746E, #  bvb_Latn_GQ
    0xB701455245746869, #  byn_Ethi_ER
    0xD701434D4C61746E, #  byv_Latn_CM
    0x93214D4C4C61746E, #  bze_Latn_ML
    0x636145534C61746E, #  ca_Latn_ES
    0x9C424E474C61746E, #  cch_Latn_NG
    0xBC42494E42656E67, #  ccp_Beng_IN
    0xBC42424443616B6D, #  ccp_Cakm_BD
    0x636552554379726C, #  ce_Cyrl_RU
    0x848250484C61746E, #  ceb_Latn_PH
    0x98C255474C61746E, #  cgg_Latn_UG
    0x636847554C61746E, #  ch_Latn_GU
    0xA8E2464D4C61746E, #  chk_Latn_FM
    0xB0E252554379726C, #  chm_Cyrl_RU
    0xB8E255534C61746E, #  cho_Latn_US
    0xBCE243414C61746E, #  chp_Latn_CA
    0xC4E2555343686572, #  chr_Cher_US
    0x81224B4841726162, #  cja_Arab_KH
    0xB122564E4368616D, #  cjm_Cham_VN
    0x8542495141726162, #  ckb_Arab_IQ
    0x636F46524C61746E, #  co_Latn_FR
    0xBDC24547436F7074, #  cop_Copt_EG
    0xC9E250484C61746E, #  cps_Latn_PH
    0x6372434143616E73, #  cr_Cans_CA
    0xA622434143616E73, #  crj_Cans_CA
    0xAA22434143616E73, #  crk_Cans_CA
    0xAE22434143616E73, #  crl_Cans_CA
    0xB222434143616E73, #  crm_Cans_CA
    0xCA2253434C61746E, #  crs_Latn_SC
    0x6373435A4C61746E, #  cs_Latn_CZ
    0x8642504C4C61746E, #  csb_Latn_PL
    0xDA42434143616E73, #  csw_Cans_CA
    0x8E624D4D50617563, #  ctd_Pauc_MM
    0x637552554379726C, #  cu_Cyrl_RU
    0x63754247476C6167, #  cu_Glag_BG
    0x637652554379726C, #  cv_Cyrl_RU
    0x637947424C61746E, #  cy_Latn_GB
    0x6461444B4C61746E, #  da_Latn_DK
    0xA80355534C61746E, #  dak_Latn_US
    0xC40352554379726C, #  dar_Cyrl_RU
    0xD4034B454C61746E, #  dav_Latn_KE
    0x8843494E41726162, #  dcc_Arab_IN
    0x646544454C61746E, #  de_Latn_DE
    0xB48343414C61746E, #  den_Latn_CA
    0xC4C343414C61746E, #  dgr_Latn_CA
    0x91234E454C61746E, #  dje_Latn_NE
    0xA5A343494C61746E, #  dnj_Latn_CI
    0xA1C3494E41726162, #  doi_Arab_IN
    0x864344454C61746E, #  dsb_Latn_DE
    0xB2634D4C4C61746E, #  dtm_Latn_ML
    0xBE634D594C61746E, #  dtp_Latn_MY
    0xE2634E5044657661, #  dty_Deva_NP
    0x8283434D4C61746E, #  dua_Latn_CM
    0x64764D5654686161, #  dv_Thaa_MV
    0xBB03534E4C61746E, #  dyo_Latn_SN
    0xD30342464C61746E, #  dyu_Latn_BF
    0x647A425454696274, #  dz_Tibt_BT
    0xD0244B454C61746E, #  ebu_Latn_KE
    0x656547484C61746E, #  ee_Latn_GH
    0xA0A44E474C61746E, #  efi_Latn_NG
    0xACC449544C61746E, #  egl_Latn_IT
    0xE0C4454745677970, #  egy_Egyp_EG
    0xE1444D4D4B616C69, #  eky_Kali_MM
    0x656C47524772656B, #  el_Grek_GR
    0x656E47424C61746E, #  en_Latn_GB
    0x656E55534C61746E, #  en_Latn_US
    0x656E474253686177, #  en_Shaw_GB
    0x657345534C61746E, #  es_Latn_ES
    0x65734D584C61746E, #  es_Latn_MX
    0x657355534C61746E, #  es_Latn_US
    0xD24455534C61746E, #  esu_Latn_US
    0x657445454C61746E, #  et_Latn_EE
    0xCE6449544974616C, #  ett_Ital_IT
    0x657545534C61746E, #  eu_Latn_ES
    0xBAC4434D4C61746E, #  ewo_Latn_CM
    0xCEE445534C61746E, #  ext_Latn_ES
    0x6661495241726162, #  fa_Arab_IR
    0xB40547514C61746E, #  fan_Latn_GQ
    0x6666474E41646C6D, #  ff_Adlm_GN
    0x6666534E4C61746E, #  ff_Latn_SN
    0xB0A54D4C4C61746E, #  ffm_Latn_ML
    0x666946494C61746E, #  fi_Latn_FI
    0x8105534441726162, #  fia_Arab_SD
    0xAD0550484C61746E, #  fil_Latn_PH
    0xCD0553454C61746E, #  fit_Latn_SE
    0x666A464A4C61746E, #  fj_Latn_FJ
    0x666F464F4C61746E, #  fo_Latn_FO
    0xB5C5424A4C61746E, #  fon_Latn_BJ
    0x667246524C61746E, #  fr_Latn_FR
    0x8A2555534C61746E, #  frc_Latn_US
    0xBE2546524C61746E, #  frp_Latn_FR
    0xC62544454C61746E, #  frr_Latn_DE
    0xCA2544454C61746E, #  frs_Latn_DE
    0x8685434D41726162, #  fub_Arab_CM
    0x8E8557464C61746E, #  fud_Latn_WF
    0x9685474E4C61746E, #  fuf_Latn_GN
    0xC2854E454C61746E, #  fuq_Latn_NE
    0xC68549544C61746E, #  fur_Latn_IT
    0xD6854E474C61746E, #  fuv_Latn_NG
    0xC6A553444C61746E, #  fvr_Latn_SD
    0x66794E4C4C61746E, #  fy_Latn_NL
    0x676149454C61746E, #  ga_Latn_IE
    0x800647484C61746E, #  gaa_Latn_GH
    0x98064D444C61746E, #  gag_Latn_MD
    0xB406434E48616E73, #  gan_Hans_CN
    0xE00649444C61746E, #  gay_Latn_ID
    0xB026494E44657661, #  gbm_Deva_IN
    0xE426495241726162, #  gbz_Arab_IR
    0xC44647464C61746E, #  gcr_Latn_GF
    0x676447424C61746E, #  gd_Latn_GB
    0xE486455445746869, #  gez_Ethi_ET
    0xB4C64E5044657661, #  ggn_Deva_NP
    0xAD064B494C61746E, #  gil_Latn_KI
    0xA926504B41726162, #  gjk_Arab_PK
    0xD126504B41726162, #  gju_Arab_PK
    0x676C45534C61746E, #  gl_Latn_ES
    0xA966495241726162, #  glk_Arab_IR
    0x676E50594C61746E, #  gn_Latn_PY
    0xB1C6494E44657661, #  gom_Deva_IN
    0xB5C6494E54656C75, #  gon_Telu_IN
    0xC5C649444C61746E, #  gor_Latn_ID
    0xC9C64E4C4C61746E, #  gos_Latn_NL
    0xCDC65541476F7468, #  got_Goth_UA
    0x8A26435943707274, #  grc_Cprt_CY
    0x8A2647524C696E62, #  grc_Linb_GR
    0xCE26494E42656E67, #  grt_Beng_IN
    0xDA4643484C61746E, #  gsw_Latn_CH
    0x6775494E47756A72, #  gu_Gujr_IN
    0x868642524C61746E, #  gub_Latn_BR
    0x8A86434F4C61746E, #  guc_Latn_CO
    0xC68647484C61746E, #  gur_Latn_GH
    0xE6864B454C61746E, #  guz_Latn_KE
    0x6776494D4C61746E, #  gv_Latn_IM
    0xC6A64E5044657661, #  gvr_Deva_NP
    0xA2C643414C61746E, #  gwi_Latn_CA
    0x68614E474C61746E, #  ha_Latn_NG
    0xA807434E48616E73, #  hak_Hans_CN
    0xD80755534C61746E, #  haw_Latn_US
    0xE407414641726162, #  haz_Arab_AF
    0x6865494C48656272, #  he_Hebr_IL
    0x6869494E44657661, #  hi_Deva_IN
    0x9507464A4C61746E, #  hif_Latn_FJ
    0xAD0750484C61746E, #  hil_Latn_PH
    0xD1675452486C7577, #  hlu_Hluw_TR
    0x8D87434E506C7264, #  hmd_Plrd_CN
    0x8DA7504B41726162, #  hnd_Arab_PK
    0x91A7494E44657661, #  hne_Deva_IN
    0xA5A74C41486D6E67, #  hnj_Hmng_LA
    0xB5A750484C61746E, #  hnn_Latn_PH
    0xB9A7504B41726162, #  hno_Arab_PK
    0x686F50474C61746E, #  ho_Latn_PG
    0x89C7494E44657661, #  hoc_Deva_IN
    0xA5C7494E44657661, #  hoj_Deva_IN
    0x687248524C61746E, #  hr_Latn_HR
    0x864744454C61746E, #  hsb_Latn_DE
    0xB647434E48616E73, #  hsn_Hans_CN
    0x687448544C61746E, #  ht_Latn_HT
    0x687548554C61746E, #  hu_Latn_HU
    0x6879414D41726D6E, #  hy_Armn_AM
    0x687A4E414C61746E, #  hz_Latn_NA
    0x696146524C61746E, #  ia_Latn_FR
    0x80284D594C61746E, #  iba_Latn_MY
    0x84284E474C61746E, #  ibb_Latn_NG
    0x696449444C61746E, #  id_Latn_ID
    0x69674E474C61746E, #  ig_Latn_NG
    0x6969434E59696969, #  ii_Yiii_CN
    0x696B55534C61746E, #  ik_Latn_US
    0xCD4843414C61746E, #  ikt_Latn_CA
    0xB96850484C61746E, #  ilo_Latn_PH
    0x696E49444C61746E, #  in_Latn_ID
    0x9DA852554379726C, #  inh_Cyrl_RU
    0x697349534C61746E, #  is_Latn_IS
    0x697449544C61746E, #  it_Latn_IT
    0x6975434143616E73, #  iu_Cans_CA
    0x6977494C48656272, #  iw_Hebr_IL
    0x9F2852554C61746E, #  izh_Latn_RU
    0x6A614A504A70616E, #  ja_Jpan_JP
    0xB0094A4D4C61746E, #  jam_Latn_JM
    0xB8C9434D4C61746E, #  jgo_Latn_CM
    0x8989545A4C61746E, #  jmc_Latn_TZ
    0xAD894E5044657661, #  jml_Deva_NP
    0xCE89444B4C61746E, #  jut_Latn_DK
    0x6A7649444C61746E, #  jv_Latn_ID
    0x6A7749444C61746E, #  jw_Latn_ID
    0x6B61474547656F72, #  ka_Geor_GE
    0x800A555A4379726C, #  kaa_Cyrl_UZ
    0x840A445A4C61746E, #  kab_Latn_DZ
    0x880A4D4D4C61746E, #  kac_Latn_MM
    0xA40A4E474C61746E, #  kaj_Latn_NG
    0xB00A4B454C61746E, #  kam_Latn_KE
    0xB80A4D4C4C61746E, #  kao_Latn_ML
    0x8C2A52554379726C, #  kbd_Cyrl_RU
    0xE02A4E4541726162, #  kby_Arab_NE
    0x984A4E474C61746E, #  kcg_Latn_NG
    0xA84A5A574C61746E, #  kck_Latn_ZW
    0x906A545A4C61746E, #  kde_Latn_TZ
    0x9C6A544741726162, #  kdh_Arab_TG
    0xCC6A544854686169, #  kdt_Thai_TH
    0x808A43564C61746E, #  kea_Latn_CV
    0xB48A434D4C61746E, #  ken_Latn_CM
    0xB8AA43494C61746E, #  kfo_Latn_CI
    0xC4AA494E44657661, #  kfr_Deva_IN
    0xE0AA494E44657661, #  kfy_Deva_IN
    0x6B6743444C61746E, #  kg_Latn_CD
    0x90CA49444C61746E, #  kge_Latn_ID
    0xBCCA42524C61746E, #  kgp_Latn_BR
    0x80EA494E4C61746E, #  kha_Latn_IN
    0x84EA434E54616C75, #  khb_Talu_CN
    0xB4EA494E44657661, #  khn_Deva_IN
    0xC0EA4D4C4C61746E, #  khq_Latn_ML
    0xCCEA494E4D796D72, #  kht_Mymr_IN
    0xD8EA504B41726162, #  khw_Arab_PK
    0x6B694B454C61746E, #  ki_Latn_KE
    0xD10A54524C61746E, #  kiu_Latn_TR
    0x6B6A4E414C61746E, #  kj_Latn_NA
    0x992A4C414C616F6F, #  kjg_Laoo_LA
    0x6B6B434E41726162, #  kk_Arab_CN
    0x6B6B4B5A4379726C, #  kk_Cyrl_KZ
    0xA54A434D4C61746E, #  kkj_Latn_CM
    0x6B6C474C4C61746E, #  kl_Latn_GL
    0xB56A4B454C61746E, #  kln_Latn_KE
    0x6B6D4B484B686D72, #  km_Khmr_KH
    0x858A414F4C61746E, #  kmb_Latn_AO
    0x6B6E494E4B6E6461, #  kn_Knda_IN
    0x6B6F4B524B6F7265, #  ko_Kore_KR
    0xA1CA52554379726C, #  koi_Cyrl_RU
    0xA9CA494E44657661, #  kok_Deva_IN
    0xC9CA464D4C61746E, #  kos_Latn_FM
    0x91EA4C524C61746E, #  kpe_Latn_LR
    0x8A2A52554379726C, #  krc_Cyrl_RU
    0xA22A534C4C61746E, #  kri_Latn_SL
    0xA62A50484C61746E, #  krj_Latn_PH
    0xAE2A52554C61746E, #  krl_Latn_RU
    0xD22A494E44657661, #  kru_Deva_IN
    0x6B73494E41726162, #  ks_Arab_IN
    0x864A545A4C61746E, #  ksb_Latn_TZ
    0x964A434D4C61746E, #  ksf_Latn_CM
    0x9E4A44454C61746E, #  ksh_Latn_DE
    0x6B75495141726162, #  ku_Arab_IQ
    0x6B7554524C61746E, #  ku_Latn_TR
    0xB28A52554379726C, #  kum_Cyrl_RU
    0x6B7652554379726C, #  kv_Cyrl_RU
    0xC6AA49444C61746E, #  kvr_Latn_ID
    0xDEAA504B41726162, #  kvx_Arab_PK
    0x6B7747424C61746E, #  kw_Latn_GB
    0xB2EA544854686169, #  kxm_Thai_TH
    0xBEEA504B41726162, #  kxp_Arab_PK
    0x6B79434E41726162, #  ky_Arab_CN
    0x6B794B474379726C, #  ky_Cyrl_KG
    0x6B7954524C61746E, #  ky_Latn_TR
    0x6C6156414C61746E, #  la_Latn_VA
    0x840B47524C696E61, #  lab_Lina_GR
    0x8C0B494C48656272, #  lad_Hebr_IL
    0x980B545A4C61746E, #  lag_Latn_TZ
    0x9C0B504B41726162, #  lah_Arab_PK
    0xA40B55474C61746E, #  laj_Latn_UG
    0x6C624C554C61746E, #  lb_Latn_LU
    0x902B52554379726C, #  lbe_Cyrl_RU
    0xD82B49444C61746E, #  lbw_Latn_ID
    0xBC4B434E54686169, #  lcp_Thai_CN
    0xBC8B494E4C657063, #  lep_Lepc_IN
    0xE48B52554379726C, #  lez_Cyrl_RU
    0x6C6755474C61746E, #  lg_Latn_UG
    0x6C694E4C4C61746E, #  li_Latn_NL
    0x950B4E5044657661, #  lif_Deva_NP
    0x950B494E4C696D62, #  lif_Limb_IN
    0xA50B49544C61746E, #  lij_Latn_IT
    0xC90B434E4C697375, #  lis_Lisu_CN
    0xBD2B49444C61746E, #  ljp_Latn_ID
    0xA14B495241726162, #  lki_Arab_IR
    0xCD4B55534C61746E, #  lkt_Latn_US
    0xB58B494E54656C75, #  lmn_Telu_IN
    0xB98B49544C61746E, #  lmo_Latn_IT
    0x6C6E43444C61746E, #  ln_Latn_CD
    0x6C6F4C414C616F6F, #  lo_Laoo_LA
    0xADCB43444C61746E, #  lol_Latn_CD
    0xE5CB5A4D4C61746E, #  loz_Latn_ZM
    0x8A2B495241726162, #  lrc_Arab_IR
    0x6C744C544C61746E, #  lt_Latn_LT
    0x9A6B4C564C61746E, #  ltg_Latn_LV
    0x6C7543444C61746E, #  lu_Latn_CD
    0x828B43444C61746E, #  lua_Latn_CD
    0xBA8B4B454C61746E, #  luo_Latn_KE
    0xE28B4B454C61746E, #  luy_Latn_KE
    0xE68B495241726162, #  luz_Arab_IR
    0x6C764C564C61746E, #  lv_Latn_LV
    0xAECB544854686169, #  lwl_Thai_TH
    0x9F2B434E48616E73, #  lzh_Hans_CN
    0xE72B54524C61746E, #  lzz_Latn_TR
    0x8C0C49444C61746E, #  mad_Latn_ID
    0x940C434D4C61746E, #  maf_Latn_CM
    0x980C494E44657661, #  mag_Deva_IN
    0xA00C494E44657661, #  mai_Deva_IN
    0xA80C49444C61746E, #  mak_Latn_ID
    0xB40C474D4C61746E, #  man_Latn_GM
    0xB40C474E4E6B6F6F, #  man_Nkoo_GN
    0xC80C4B454C61746E, #  mas_Latn_KE
    0xE40C4D584C61746E, #  maz_Latn_MX
    0x946C52554379726C, #  mdf_Cyrl_RU
    0x9C6C50484C61746E, #  mdh_Latn_PH
    0xC46C49444C61746E, #  mdr_Latn_ID
    0xB48C534C4C61746E, #  men_Latn_SL
    0xC48C4B454C61746E, #  mer_Latn_KE
    0x80AC544841726162, #  mfa_Arab_TH
    0x90AC4D554C61746E, #  mfe_Latn_MU
    0x6D674D474C61746E, #  mg_Latn_MG
    0x9CCC4D5A4C61746E, #  mgh_Latn_MZ
    0xB8CC434D4C61746E, #  mgo_Latn_CM
    0xBCCC4E5044657661, #  mgp_Deva_NP
    0xE0CC545A4C61746E, #  mgy_Latn_TZ
    0x6D684D484C61746E, #  mh_Latn_MH
    0x6D694E5A4C61746E, #  mi_Latn_NZ
    0xB50C49444C61746E, #  min_Latn_ID
    0xC90C495148617472, #  mis_Hatr_IQ
    0x6D6B4D4B4379726C, #  mk_Cyrl_MK
    0x6D6C494E4D6C796D, #  ml_Mlym_IN
    0xC96C53444C61746E, #  mls_Latn_SD
    0x6D6E4D4E4379726C, #  mn_Cyrl_MN
    0x6D6E434E4D6F6E67, #  mn_Mong_CN
    0xA1AC494E42656E67, #  mni_Beng_IN
    0xD9AC4D4D4D796D72, #  mnw_Mymr_MM
    0x91CC43414C61746E, #  moe_Latn_CA
    0x9DCC43414C61746E, #  moh_Latn_CA
    0xC9CC42464C61746E, #  mos_Latn_BF
    0x6D72494E44657661, #  mr_Deva_IN
    0x8E2C4E5044657661, #  mrd_Deva_NP
    0xA62C52554379726C, #  mrj_Cyrl_RU
    0xBA2C42444D726F6F, #  mro_Mroo_BD
    0x6D734D594C61746E, #  ms_Latn_MY
    0x6D744D544C61746E, #  mt_Latn_MT
    0xC66C494E44657661, #  mtr_Deva_IN
    0x828C434D4C61746E, #  mua_Latn_CM
    0xCA8C55534C61746E, #  mus_Latn_US
    0xE2AC504B41726162, #  mvy_Arab_PK
    0xAACC4D4C4C61746E, #  mwk_Latn_ML
    0xC6CC494E44657661, #  mwr_Deva_IN
    0xD6CC49444C61746E, #  mwv_Latn_ID
    0x8AEC5A574C61746E, #  mxc_Latn_ZW
    0x6D794D4D4D796D72, #  my_Mymr_MM
    0xD70C52554379726C, #  myv_Cyrl_RU
    0xDF0C55474C61746E, #  myx_Latn_UG
    0xE70C49524D616E64, #  myz_Mand_IR
    0xB72C495241726162, #  mzn_Arab_IR
    0x6E614E524C61746E, #  na_Latn_NR
    0xB40D434E48616E73, #  nan_Hans_CN
    0xBC0D49544C61746E, #  nap_Latn_IT
    0xC00D4E414C61746E, #  naq_Latn_NA
    0x6E624E4F4C61746E, #  nb_Latn_NO
    0x9C4D4D584C61746E, #  nch_Latn_MX
    0x6E645A574C61746E, #  nd_Latn_ZW
    0x886D4D5A4C61746E, #  ndc_Latn_MZ
    0xC86D44454C61746E, #  nds_Latn_DE
    0x6E654E5044657661, #  ne_Deva_NP
    0xD88D4E5044657661, #  new_Deva_NP
    0x6E674E414C61746E, #  ng_Latn_NA
    0xACCD4D5A4C61746E, #  ngl_Latn_MZ
    0x90ED4D584C61746E, #  nhe_Latn_MX
    0xD8ED4D584C61746E, #  nhw_Latn_MX
    0xA50D49444C61746E, #  nij_Latn_ID
    0xD10D4E554C61746E, #  niu_Latn_NU
    0xB92D494E4C61746E, #  njo_Latn_IN
    0x6E6C4E4C4C61746E, #  nl_Latn_NL
    0x998D434D4C61746E, #  nmg_Latn_CM
    0x6E6E4E4F4C61746E, #  nn_Latn_NO
    0x9DAD434D4C61746E, #  nnh_Latn_CM
    0x6E6F4E4F4C61746E, #  no_Latn_NO
    0x8DCD54484C616E61, #  nod_Lana_TH
    0x91CD494E44657661, #  noe_Deva_IN
    0xB5CD534552756E72, #  non_Runr_SE
    0xBA0D474E4E6B6F6F, #  nqo_Nkoo_GN
    0x6E725A414C61746E, #  nr_Latn_ZA
    0xAA4D434143616E73, #  nsk_Cans_CA
    0xBA4D5A414C61746E, #  nso_Latn_ZA
    0xCA8D53534C61746E, #  nus_Latn_SS
    0x6E7655534C61746E, #  nv_Latn_US
    0xC2ED434E4C61746E, #  nxq_Latn_CN
    0x6E794D574C61746E, #  ny_Latn_MW
    0xB30D545A4C61746E, #  nym_Latn_TZ
    0xB70D55474C61746E, #  nyn_Latn_UG
    0xA32D47484C61746E, #  nzi_Latn_GH
    0x6F6346524C61746E, #  oc_Latn_FR
    0x6F6D45544C61746E, #  om_Latn_ET
    0x6F72494E4F727961, #  or_Orya_IN
    0x6F7347454379726C, #  os_Cyrl_GE
    0x824E55534F736765, #  osa_Osge_US
    0xAA6E4D4E4F726B68, #  otk_Orkh_MN
    0x7061504B41726162, #  pa_Arab_PK
    0x7061494E47757275, #  pa_Guru_IN
    0x980F50484C61746E, #  pag_Latn_PH
    0xAC0F495250686C69, #  pal_Phli_IR
    0xAC0F434E50686C70, #  pal_Phlp_CN
    0xB00F50484C61746E, #  pam_Latn_PH
    0xBC0F41574C61746E, #  pap_Latn_AW
    0xD00F50574C61746E, #  pau_Latn_PW
    0x8C4F46524C61746E, #  pcd_Latn_FR
    0xB04F4E474C61746E, #  pcm_Latn_NG
    0x886F55534C61746E, #  pdc_Latn_US
    0xCC6F43414C61746E, #  pdt_Latn_CA
    0xB88F49525870656F, #  peo_Xpeo_IR
    0xACAF44454C61746E, #  pfl_Latn_DE
    0xB4EF4C4250686E78, #  phn_Phnx_LB
    0x814F494E42726168, #  pka_Brah_IN
    0xB94F4B454C61746E, #  pko_Latn_KE
    0x706C504C4C61746E, #  pl_Latn_PL
    0xC98F49544C61746E, #  pms_Latn_IT
    0xCDAF47524772656B, #  pnt_Grek_GR
    0xB5CF464D4C61746E, #  pon_Latn_FM
    0x822F504B4B686172, #  pra_Khar_PK
    0x8E2F495241726162, #  prd_Arab_IR
    0x7073414641726162, #  ps_Arab_AF
    0x707442524C61746E, #  pt_Latn_BR
    0xD28F47414C61746E, #  puu_Latn_GA
    0x717550454C61746E, #  qu_Latn_PE
    0x8A9047544C61746E, #  quc_Latn_GT
    0x9A9045434C61746E, #  qug_Latn_EC
    0xA411494E44657661, #  raj_Deva_IN
    0x945152454C61746E, #  rcf_Latn_RE
    0xA49149444C61746E, #  rej_Latn_ID
    0xB4D149544C61746E, #  rgn_Latn_IT
    0x8111494E4C61746E, #  ria_Latn_IN
    0x95114D4154666E67, #  rif_Tfng_MA
    0xC9314E5044657661, #  rjs_Deva_NP
    0xCD51424442656E67, #  rkt_Beng_BD
    0x726D43484C61746E, #  rm_Latn_CH
    0x959146494C61746E, #  rmf_Latn_FI
    0xB99143484C61746E, #  rmo_Latn_CH
    0xCD91495241726162, #  rmt_Arab_IR
    0xD19153454C61746E, #  rmu_Latn_SE
    0x726E42494C61746E, #  rn_Latn_BI
    0x99B14D5A4C61746E, #  rng_Latn_MZ
    0x726F524F4C61746E, #  ro_Latn_RO
    0x85D149444C61746E, #  rob_Latn_ID
    0x95D1545A4C61746E, #  rof_Latn_TZ
    0xB271464A4C61746E, #  rtm_Latn_FJ
    0x727552554379726C, #  ru_Cyrl_RU
    0x929155414379726C, #  rue_Cyrl_UA
    0x9A9153424C61746E, #  rug_Latn_SB
    0x727752574C61746E, #  rw_Latn_RW
    0xAAD1545A4C61746E, #  rwk_Latn_TZ
    0xD3114A504B616E61, #  ryu_Kana_JP
    0x7361494E44657661, #  sa_Deva_IN
    0x941247484C61746E, #  saf_Latn_GH
    0x9C1252554379726C, #  sah_Cyrl_RU
    0xC0124B454C61746E, #  saq_Latn_KE
    0xC81249444C61746E, #  sas_Latn_ID
    0xCC12494E4C61746E, #  sat_Latn_IN
    0xE412494E53617572, #  saz_Saur_IN
    0xBC32545A4C61746E, #  sbp_Latn_TZ
    0x736349544C61746E, #  sc_Latn_IT
    0xA852494E44657661, #  sck_Deva_IN
    0xB45249544C61746E, #  scn_Latn_IT
    0xB85247424C61746E, #  sco_Latn_GB
    0xC85243414C61746E, #  scs_Latn_CA
    0x7364504B41726162, #  sd_Arab_PK
    0x7364494E44657661, #  sd_Deva_IN
    0x7364494E4B686F6A, #  sd_Khoj_IN
    0x7364494E53696E64, #  sd_Sind_IN
    0x887249544C61746E, #  sdc_Latn_IT
    0x9C72495241726162, #  sdh_Arab_IR
    0x73654E4F4C61746E, #  se_Latn_NO
    0x949243494C61746E, #  sef_Latn_CI
    0x9C924D5A4C61746E, #  seh_Latn_MZ
    0xA0924D584C61746E, #  sei_Latn_MX
    0xC8924D4C4C61746E, #  ses_Latn_ML
    0x736743464C61746E, #  sg_Latn_CF
    0x80D249454F67616D, #  sga_Ogam_IE
    0xC8D24C544C61746E, #  sgs_Latn_LT
    0xA0F24D4154666E67, #  shi_Tfng_MA
    0xB4F24D4D4D796D72, #  shn_Mymr_MM
    0x73694C4B53696E68, #  si_Sinh_LK
    0x8D1245544C61746E, #  sid_Latn_ET
    0x736B534B4C61746E, #  sk_Latn_SK
    0xC552504B41726162, #  skr_Arab_PK
    0x736C53494C61746E, #  sl_Latn_SI
    0xA172504C4C61746E, #  sli_Latn_PL
    0xE17249444C61746E, #  sly_Latn_ID
    0x736D57534C61746E, #  sm_Latn_WS
    0x819253454C61746E, #  sma_Latn_SE
    0xA59253454C61746E, #  smj_Latn_SE
    0xB59246494C61746E, #  smn_Latn_FI
    0xBD92494C53616D72, #  smp_Samr_IL
    0xC99246494C61746E, #  sms_Latn_FI
    0x736E5A574C61746E, #  sn_Latn_ZW
    0xA9B24D4C4C61746E, #  snk_Latn_ML
    0x736F534F4C61746E, #  so_Latn_SO
    0xD1D2544854686169, #  sou_Thai_TH
    0x7371414C4C61746E, #  sq_Latn_AL
    0x737252534379726C, #  sr_Cyrl_RS
    0x737252534C61746E, #  sr_Latn_RS
    0x8632494E536F7261, #  srb_Sora_IN
    0xB63253524C61746E, #  srn_Latn_SR
    0xC632534E4C61746E, #  srr_Latn_SN
    0xDE32494E44657661, #  srx_Deva_IN
    0x73735A414C61746E, #  ss_Latn_ZA
    0xE25245524C61746E, #  ssy_Latn_ER
    0x73745A414C61746E, #  st_Latn_ZA
    0xC27244454C61746E, #  stq_Latn_DE
    0x737549444C61746E, #  su_Latn_ID
    0xAA92545A4C61746E, #  suk_Latn_TZ
    0xCA92474E4C61746E, #  sus_Latn_GN
    0x737653454C61746E, #  sv_Latn_SE
    0x7377545A4C61746E, #  sw_Latn_TZ
    0x86D2595441726162, #  swb_Arab_YT
    0x8AD243444C61746E, #  swc_Latn_CD
    0x9AD244454C61746E, #  swg_Latn_DE
    0xD6D2494E44657661, #  swv_Deva_IN
    0xB6F249444C61746E, #  sxn_Latn_ID
    0xAF12424442656E67, #  syl_Beng_BD
    0xC712495153797263, #  syr_Syrc_IQ
    0xAF32504C4C61746E, #  szl_Latn_PL
    0x7461494E54616D6C, #  ta_Taml_IN
    0xA4134E5044657661, #  taj_Deva_NP
    0xD83350484C61746E, #  tbw_Latn_PH
    0xE053494E4B6E6461, #  tcy_Knda_IN
    0x8C73434E54616C65, #  tdd_Tale_CN
    0x98734E5044657661, #  tdg_Deva_NP
    0x9C734E5044657661, #  tdh_Deva_NP
    0x7465494E54656C75, #  te_Telu_IN
    0xB093534C4C61746E, #  tem_Latn_SL
    0xB89355474C61746E, #  teo_Latn_UG
    0xCC93544C4C61746E, #  tet_Latn_TL
    0x7467504B41726162, #  tg_Arab_PK
    0x7467544A4379726C, #  tg_Cyrl_TJ
    0x7468544854686169, #  th_Thai_TH
    0xACF34E5044657661, #  thl_Deva_NP
    0xC0F34E5044657661, #  thq_Deva_NP
    0xC4F34E5044657661, #  thr_Deva_NP
    0x7469455445746869, #  ti_Ethi_ET
    0x9913455245746869, #  tig_Ethi_ER
    0xD5134E474C61746E, #  tiv_Latn_NG
    0x746B544D4C61746E, #  tk_Latn_TM
    0xAD53544B4C61746E, #  tkl_Latn_TK
    0xC553415A4C61746E, #  tkr_Latn_AZ
    0xCD534E5044657661, #  tkt_Deva_NP
    0x746C50484C61746E, #  tl_Latn_PH
    0xE173415A4C61746E, #  tly_Latn_AZ
    0x9D934E454C61746E, #  tmh_Latn_NE
    0x746E5A414C61746E, #  tn_Latn_ZA
    0x746F544F4C61746E, #  to_Latn_TO
    0x99D34D574C61746E, #  tog_Latn_MW
    0xA1F350474C61746E, #  tpi_Latn_PG
    0x747254524C61746E, #  tr_Latn_TR
    0xD23354524C61746E, #  tru_Latn_TR
    0xD63354574C61746E, #  trv_Latn_TW
    0x74735A414C61746E, #  ts_Latn_ZA
    0x8E5347524772656B, #  tsd_Grek_GR
    0x96534E5044657661, #  tsf_Deva_NP
    0x9A5350484C61746E, #  tsg_Latn_PH
    0xA653425454696274, #  tsj_Tibt_BT
    0x747452554379726C, #  tt_Cyrl_RU
    0xA67355474C61746E, #  ttj_Latn_UG
    0xCA73544854686169, #  tts_Thai_TH
    0xCE73415A4C61746E, #  ttt_Latn_AZ
    0xB2934D574C61746E, #  tum_Latn_MW
    0xAEB354564C61746E, #  tvl_Latn_TV
    0xC2D34E454C61746E, #  twq_Latn_NE
    0x9AF3434E54616E67, #  txg_Tang_CN
    0x747950464C61746E, #  ty_Latn_PF
    0xD71352554379726C, #  tyv_Cyrl_RU
    0xB3334D414C61746E, #  tzm_Latn_MA
    0xB07452554379726C, #  udm_Cyrl_RU
    0x7567434E41726162, #  ug_Arab_CN
    0x75674B5A4379726C, #  ug_Cyrl_KZ
    0x80D4535955676172, #  uga_Ugar_SY
    0x756B55414379726C, #  uk_Cyrl_UA
    0xA174464D4C61746E, #  uli_Latn_FM
    0x8594414F4C61746E, #  umb_Latn_AO
    0xC5B4494E42656E67, #  unr_Beng_IN
    0xC5B44E5044657661, #  unr_Deva_NP
    0xDDB4494E42656E67, #  unx_Beng_IN
    0x7572504B41726162, #  ur_Arab_PK
    0x757A414641726162, #  uz_Arab_AF
    0x757A555A4C61746E, #  uz_Latn_UZ
    0xA0154C5256616969, #  vai_Vaii_LR
    0x76655A414C61746E, #  ve_Latn_ZA
    0x889549544C61746E, #  vec_Latn_IT
    0xBC9552554C61746E, #  vep_Latn_RU
    0x7669564E4C61746E, #  vi_Latn_VN
    0x891553584C61746E, #  vic_Latn_SX
    0xC97542454C61746E, #  vls_Latn_BE
    0x959544454C61746E, #  vmf_Latn_DE
    0xD9954D5A4C61746E, #  vmw_Latn_MZ
    0xCDD552554C61746E, #  vot_Latn_RU
    0xBA3545454C61746E, #  vro_Latn_EE
    0xB695545A4C61746E, #  vun_Latn_TZ
    0x776142454C61746E, #  wa_Latn_BE
    0x901643484C61746E, #  wae_Latn_CH
    0xAC16455445746869, #  wal_Ethi_ET
    0xC41650484C61746E, #  war_Latn_PH
    0xBC3641554C61746E, #  wbp_Latn_AU
    0xC036494E54656C75, #  wbq_Telu_IN
    0xC436494E44657661, #  wbr_Deva_IN
    0xC97657464C61746E, #  wls_Latn_WF
    0xA1B64B4D41726162, #  wni_Arab_KM
    0x776F534E4C61746E, #  wo_Latn_SN
    0xB276494E44657661, #  wtm_Deva_IN
    0xD296434E48616E73, #  wuu_Hans_CN
    0xD41742524C61746E, #  xav_Latn_BR
    0xC457545243617269, #  xcr_Cari_TR
    0x78685A414C61746E, #  xh_Latn_ZA
    0x897754524C796369, #  xlc_Lyci_TR
    0x8D7754524C796469, #  xld_Lydi_TR
    0x9597474547656F72, #  xmf_Geor_GE
    0xB597434E4D616E69, #  xmn_Mani_CN
    0xC59753444D657263, #  xmr_Merc_SD
    0x81B753414E617262, #  xna_Narb_SA
    0xC5B7494E44657661, #  xnr_Deva_IN
    0x99D755474C61746E, #  xog_Latn_UG
    0xC5F7495250727469, #  xpr_Prti_IR
    0x8257594553617262, #  xsa_Sarb_YE
    0xC6574E5044657661, #  xsr_Deva_NP
    0xB8184D5A4C61746E, #  yao_Latn_MZ
    0xBC18464D4C61746E, #  yap_Latn_FM
    0xD418434D4C61746E, #  yav_Latn_CM
    0x8438434D4C61746E, #  ybb_Latn_CM
    0x796F4E474C61746E, #  yo_Latn_NG
    0xAE3842524C61746E, #  yrl_Latn_BR
    0x82984D584C61746E, #  yua_Latn_MX
    0x9298434E48616E73, #  yue_Hans_CN
    0x9298484B48616E74, #  yue_Hant_HK
    0x7A61434E4C61746E, #  za_Latn_CN
    0x981953444C61746E, #  zag_Latn_SD
    0xA4794B4D41726162, #  zdj_Arab_KM
    0x80994E4C4C61746E, #  zea_Latn_NL
    0x9CD94D4154666E67, #  zgh_Tfng_MA
    0x7A685457426F706F, #  zh_Bopo_TW
    0x7A68545748616E62, #  zh_Hanb_TW
    0x7A68434E48616E73, #  zh_Hans_CN
    0x7A68545748616E74, #  zh_Hant_TW
    0xB17954474C61746E, #  zlm_Latn_TG
    0xA1994D594C61746E, #  zmi_Latn_MY
    0x7A755A414C61746E, #  zu_Latn_ZA
    0x833954524C61746E, #  zza_Latn_TR
]

ARAB_PARENTS = dict([
    (0x6172445A, 0x61729420), #  ar-DZ -> ar-015
    (0x61724548, 0x61729420), #  ar-EH -> ar-015
    (0x61724C59, 0x61729420), #  ar-LY -> ar-015
    (0x61724D41, 0x61729420), #  ar-MA -> ar-015
    (0x6172544E, 0x61729420), #  ar-TN -> ar-015
])

HANT_PARENTS = dict([
    (0x7A684D4F, 0x7A68484B), #  zh-Hant-MO -> zh-Hant-HK
])

LATN_PARENTS = dict([
    (0x656E80A1, 0x656E8400), #  en-150 -> en-001
    (0x656E4147, 0x656E8400), #  en-AG -> en-001
    (0x656E4149, 0x656E8400), #  en-AI -> en-001
    (0x656E4154, 0x656E80A1), #  en-AT -> en-150
    (0x656E4155, 0x656E8400), #  en-AU -> en-001
    (0x656E4242, 0x656E8400), #  en-BB -> en-001
    (0x656E4245, 0x656E8400), #  en-BE -> en-001
    (0x656E424D, 0x656E8400), #  en-BM -> en-001
    (0x656E4253, 0x656E8400), #  en-BS -> en-001
    (0x656E4257, 0x656E8400), #  en-BW -> en-001
    (0x656E425A, 0x656E8400), #  en-BZ -> en-001
    (0x656E4341, 0x656E8400), #  en-CA -> en-001
    (0x656E4343, 0x656E8400), #  en-CC -> en-001
    (0x656E4348, 0x656E80A1), #  en-CH -> en-150
    (0x656E434B, 0x656E8400), #  en-CK -> en-001
    (0x656E434D, 0x656E8400), #  en-CM -> en-001
    (0x656E4358, 0x656E8400), #  en-CX -> en-001
    (0x656E4359, 0x656E8400), #  en-CY -> en-001
    (0x656E4445, 0x656E80A1), #  en-DE -> en-150
    (0x656E4447, 0x656E8400), #  en-DG -> en-001
    (0x656E444B, 0x656E80A1), #  en-DK -> en-150
    (0x656E444D, 0x656E8400), #  en-DM -> en-001
    (0x656E4552, 0x656E8400), #  en-ER -> en-001
    (0x656E4649, 0x656E80A1), #  en-FI -> en-150
    (0x656E464A, 0x656E8400), #  en-FJ -> en-001
    (0x656E464B, 0x656E8400), #  en-FK -> en-001
    (0x656E464D, 0x656E8400), #  en-FM -> en-001
    (0x656E4742, 0x656E8400), #  en-GB -> en-001
    (0x656E4744, 0x656E8400), #  en-GD -> en-001
    (0x656E4747, 0x656E8400), #  en-GG -> en-001
    (0x656E4748, 0x656E8400), #  en-GH -> en-001
    (0x656E4749, 0x656E8400), #  en-GI -> en-001
    (0x656E474D, 0x656E8400), #  en-GM -> en-001
    (0x656E4759, 0x656E8400), #  en-GY -> en-001
    (0x656E484B, 0x656E8400), #  en-HK -> en-001
    (0x656E4945, 0x656E8400), #  en-IE -> en-001
    (0x656E494C, 0x656E8400), #  en-IL -> en-001
    (0x656E494D, 0x656E8400), #  en-IM -> en-001
    (0x656E494E, 0x656E8400), #  en-IN -> en-001
    (0x656E494F, 0x656E8400), #  en-IO -> en-001
    (0x656E4A45, 0x656E8400), #  en-JE -> en-001
    (0x656E4A4D, 0x656E8400), #  en-JM -> en-001
    (0x656E4B45, 0x656E8400), #  en-KE -> en-001
    (0x656E4B49, 0x656E8400), #  en-KI -> en-001
    (0x656E4B4E, 0x656E8400), #  en-KN -> en-001
    (0x656E4B59, 0x656E8400), #  en-KY -> en-001
    (0x656E4C43, 0x656E8400), #  en-LC -> en-001
    (0x656E4C52, 0x656E8400), #  en-LR -> en-001
    (0x656E4C53, 0x656E8400), #  en-LS -> en-001
    (0x656E4D47, 0x656E8400), #  en-MG -> en-001
    (0x656E4D4F, 0x656E8400), #  en-MO -> en-001
    (0x656E4D53, 0x656E8400), #  en-MS -> en-001
    (0x656E4D54, 0x656E8400), #  en-MT -> en-001
    (0x656E4D55, 0x656E8400), #  en-MU -> en-001
    (0x656E4D57, 0x656E8400), #  en-MW -> en-001
    (0x656E4D59, 0x656E8400), #  en-MY -> en-001
    (0x656E4E41, 0x656E8400), #  en-NA -> en-001
    (0x656E4E46, 0x656E8400), #  en-NF -> en-001
    (0x656E4E47, 0x656E8400), #  en-NG -> en-001
    (0x656E4E4C, 0x656E80A1), #  en-NL -> en-150
    (0x656E4E52, 0x656E8400), #  en-NR -> en-001
    (0x656E4E55, 0x656E8400), #  en-NU -> en-001
    (0x656E4E5A, 0x656E8400), #  en-NZ -> en-001
    (0x656E5047, 0x656E8400), #  en-PG -> en-001
    (0x656E5048, 0x656E8400), #  en-PH -> en-001
    (0x656E504B, 0x656E8400), #  en-PK -> en-001
    (0x656E504E, 0x656E8400), #  en-PN -> en-001
    (0x656E5057, 0x656E8400), #  en-PW -> en-001
    (0x656E5257, 0x656E8400), #  en-RW -> en-001
    (0x656E5342, 0x656E8400), #  en-SB -> en-001
    (0x656E5343, 0x656E8400), #  en-SC -> en-001
    (0x656E5344, 0x656E8400), #  en-SD -> en-001
    (0x656E5345, 0x656E80A1), #  en-SE -> en-150
    (0x656E5347, 0x656E8400), #  en-SG -> en-001
    (0x656E5348, 0x656E8400), #  en-SH -> en-001
    (0x656E5349, 0x656E80A1), #  en-SI -> en-150
    (0x656E534C, 0x656E8400), #  en-SL -> en-001
    (0x656E5353, 0x656E8400), #  en-SS -> en-001
    (0x656E5358, 0x656E8400), #  en-SX -> en-001
    (0x656E535A, 0x656E8400), #  en-SZ -> en-001
    (0x656E5443, 0x656E8400), #  en-TC -> en-001
    (0x656E544B, 0x656E8400), #  en-TK -> en-001
    (0x656E544F, 0x656E8400), #  en-TO -> en-001
    (0x656E5454, 0x656E8400), #  en-TT -> en-001
    (0x656E5456, 0x656E8400), #  en-TV -> en-001
    (0x656E545A, 0x656E8400), #  en-TZ -> en-001
    (0x656E5547, 0x656E8400), #  en-UG -> en-001
    (0x656E5643, 0x656E8400), #  en-VC -> en-001
    (0x656E5647, 0x656E8400), #  en-VG -> en-001
    (0x656E5655, 0x656E8400), #  en-VU -> en-001
    (0x656E5753, 0x656E8400), #  en-WS -> en-001
    (0x656E5A41, 0x656E8400), #  en-ZA -> en-001
    (0x656E5A4D, 0x656E8400), #  en-ZM -> en-001
    (0x656E5A57, 0x656E8400), #  en-ZW -> en-001
    (0x65734152, 0x6573A424), #  es-AR -> es-419
    (0x6573424F, 0x6573A424), #  es-BO -> es-419
    (0x65734252, 0x6573A424), #  es-BR -> es-419
    (0x6573434C, 0x6573A424), #  es-CL -> es-419
    (0x6573434F, 0x6573A424), #  es-CO -> es-419
    (0x65734352, 0x6573A424), #  es-CR -> es-419
    (0x65734355, 0x6573A424), #  es-CU -> es-419
    (0x6573444F, 0x6573A424), #  es-DO -> es-419
    (0x65734543, 0x6573A424), #  es-EC -> es-419
    (0x65734754, 0x6573A424), #  es-GT -> es-419
    (0x6573484E, 0x6573A424), #  es-HN -> es-419
    (0x65734D58, 0x6573A424), #  es-MX -> es-419
    (0x65734E49, 0x6573A424), #  es-NI -> es-419
    (0x65735041, 0x6573A424), #  es-PA -> es-419
    (0x65735045, 0x6573A424), #  es-PE -> es-419
    (0x65735052, 0x6573A424), #  es-PR -> es-419
    (0x65735059, 0x6573A424), #  es-PY -> es-419
    (0x65735356, 0x6573A424), #  es-SV -> es-419
    (0x65735553, 0x6573A424), #  es-US -> es-419
    (0x65735559, 0x6573A424), #  es-UY -> es-419
    (0x65735645, 0x6573A424), #  es-VE -> es-419
    (0x7074414F, 0x70745054), #  pt-AO -> pt-PT
    (0x70744348, 0x70745054), #  pt-CH -> pt-PT
    (0x70744356, 0x70745054), #  pt-CV -> pt-PT
    (0x70744751, 0x70745054), #  pt-GQ -> pt-PT
    (0x70744757, 0x70745054), #  pt-GW -> pt-PT
    (0x70744C55, 0x70745054), #  pt-LU -> pt-PT
    (0x70744D4F, 0x70745054), #  pt-MO -> pt-PT
    (0x70744D5A, 0x70745054), #  pt-MZ -> pt-PT
    (0x70745354, 0x70745054), #  pt-ST -> pt-PT
    (0x7074544C, 0x70745054), #  pt-TL -> pt-PT
])

SCRIPT_PARENTS = dict([
    ('Arab', ARAB_PARENTS),
    ('Hant', HANT_PARENTS),
    ('Latn', LATN_PARENTS),
])

MAX_PARENT_DEPTH = 3

