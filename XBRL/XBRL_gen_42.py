'''
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree
'''
from lxml import etree
import re
import sys
import os
import shutil
import gc
import time
import csv
import uuid
import json
import datetime
from datetime import timedelta, date
from PyQt5.QtGui     import *
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
import PySimpleGUI as sg

taxonomy_dict = {"008-ALL":'Valyuta_008AllLekMember', "012-DZD":'Valyuta_012DzdAlzhirskijDinarMember', "032-ARS":'Valyuta_032ArsArgentinskoePesoMember', "036-AUD":'Valyuta_036AudAvstralijskijDollarMember', "044-BSD":'Valyuta_044BsdBagamskijDollarMember', "048-BHD":'Valyuta_048BhdBaxrejnskijDinarMember', "050-BDT":'Valyuta_050BdtTakaMember', "051-AMD":'Valyuta_051AmdArmyanskijDramMember', "052-BBD":'Valyuta_052BbdBarbadosskijDollarMember', "060-BMD":'Valyuta_060BmdBermudskijDollarMember', "064-BTN":'Valyuta_064BtnNgultrumMember', "068-BOB":'Valyuta_068BobBolivianoMember', "072-BWP":'Valyuta_072BwpPulaMember', "084-BZD":'Valyuta_084BzdBelizskijDollarMember', "090-SBD":'Valyuta_090SbdDollarSolomonovyxOstrovovMember', "096-BND":'Valyuta_096BndBrunejskijDollarMember', "104-MMK":'Valyuta_104MmkKyatMember', "108-BIF":'Valyuta_108BifBurundijskijFrankMember', "116-KHR":'Valyuta_116KhrRielMember', "124-CAD":'Valyuta_124CadKanadskijDollarMember', "132-CVE":'Valyuta_132CveEskudoKaboVerdeMember', "136-KYD":'Valyuta_136KydDollarOstrovovKajmanMember', "144-LKR":'Valyuta_144LkrSHriLankijskayaRupiyaMember', "152-CLP":'Valyuta_152ClpCHilijskoePesoMember', "156-CNY":'Valyuta_156CnyYUanMember', "170-COP":'Valyuta_170CopKolumbijskoePesoMember', "174-KMF":'Valyuta_174KmfFrankKomorMember', "188-CRC":'Valyuta_188CrcKostarikanskijKolonMember', "191-HRK":'Valyuta_191HrkKunaMember', "192-CUP":'Valyuta_192CupKubinskoePesoMember', "203-CZK":'Valyuta_203CzkCHeshskayaKronaMember', "208-DKK":'Valyuta_208DkkDatskayaKronaMember', "214-DOP":'Valyuta_214DopDominikanskoePesoMember', "222-SVC":'Valyuta_222SvcSalvadorskijKolonMember', "230-ETB":'Valyuta_230EtbEfiopskijByrMember', "232-ERN":'Valyuta_232ErnNakfaMember', "238-FKP":'Valyuta_238FkpFuntFolklendskixOstrovovMember', "242-FJD":'Valyuta_242FjdDollarFidzhiMember', "262-DJF":'Valyuta_262DjfFrankDzhibutiMember', "270-GMD":'Valyuta_270GmdDalasiMember', "292-GIP":'Valyuta_292GipGibraltarskijFuntMember', "320-GTQ":'Valyuta_320GtqKetsalMember', "324-GNF":'Valyuta_324GnfGvinejskijFrankMember', "328-GYD":'Valyuta_328GydGajanskijDollarMember', "332-HTG":'Valyuta_332HtgGurdMember', "340-HNL":'Valyuta_340HnlLempiraMember', "344-HKD":'Valyuta_344HkdGonkongskijDollarMember', "348-HUF":'Valyuta_348HufForintMember', "352-ISK":'Valyuta_352IskIslandskayaKronaMember', "356-INR":'Valyuta_356InrIndijskayaRupiyaMember', "360-IDR":'Valyuta_360IdrRupiyaMember', "364-IRR":'Valyuta_364IrrIranskijRialMember', "368-IQD":'Valyuta_368IqdIrakskijDinarMember', "376-ILS":'Valyuta_376IlsNovyjIzrailskijSHekelMember', "388-JMD":'Valyuta_388JmdYAmajskijDollarMember', "392-JPY":'Valyuta_392JpyIenaMember', "398-KZT":'Valyuta_398KztTengeMember', "400-JOD":'Valyuta_400JodIordanskijDinarMember', "404-KES":'Valyuta_404KesKenijskijSHillingMember', "408-KPW":'Valyuta_408KpwSeverokorejskayaVonaMember', "410-KRW":'Valyuta_410KrwVonaMember', "414-KWD":'Valyuta_414KwdKuvejtskijDinarMember', "417-KGS":'Valyuta_417KgsSomMember', "418-LAK":'Valyuta_418LakKipMember', "422-LBP":'Valyuta_422LbpLivanskijFuntMember', "426-LSL":'Valyuta_426LslLotiMember', "430-LRD":'Valyuta_430LrdLiberijskijDollarMember', "434-LYD":'Valyuta_434LydLivijskijDinarMember', "446-MOP":'Valyuta_446MopPatakaMember', "454-MWK":'Valyuta_454MwkKvachaMember', "458-MYR":'Valyuta_458MyrMalajzijskijRinggitMember', "462-MVR":'Valyuta_462MvrRufiyaMember', "480-MUR":'Valyuta_480MurMavrikijskayaRupiyaMember', "484-MXN":'Valyuta_484MxnMeksikanskoePesoMember', "496-MNT":'Valyuta_496MntTugrikMember', "498-MDL":'Valyuta_498MdlMoldavskijLejMember', "504-MAD":'Valyuta_504MadMarokkanskijDirxamMember', "512-OMR":'Valyuta_512OmrOmanskijRialMember', "516-NAD":'Valyuta_516NadDollarNamibiiMember', "524-NPR":'Valyuta_524NprNepalskayaRupiyaMember', "532-ANG":'Valyuta_532AngNiderlandskijAntilskijGuldenMember', "533-AWG":'Valyuta_533AwgArubanskijFlorinMember', "548-VUV":'Valyuta_548VuvVatuMember', "554-NZD":'Valyuta_554NzdNovozelandskijDollarMember', "558-NIO":'Valyuta_558NioZolotayaKordobaMember', "566-NGN":'Valyuta_566NgnNajraMember', "578-NOK":'Valyuta_578NokNorvezhskayaKronaMember', "586-PKR":'Valyuta_586PkrPakistanskayaRupiyaMember', "590-PAB":'Valyuta_590PabBalboaMember', "598-PGK":'Valyuta_598PgkKinaMember', "600-PYG":'Valyuta_600PygGuaraniMember', "604-PEN":'Valyuta_604PenNovyjSolMember', "608-PHP":'Valyuta_608PhpFilippinskoePesoMember', "634-QAR":'Valyuta_634QarKatarskijRialMember', "643-RUB":'Valyuta_643RubRossijskijRublMember', "646-RWF":'Valyuta_646RwfFrankRuandyMember', "654-SHP":'Valyuta_654ShpFuntSvyatojElenyMember', "682-SAR":'Valyuta_682SarSaudovskijRiyalMember', "690-SCR":'Valyuta_690ScrSejshelskayaRupiyaMember', "694-SLL":'Valyuta_694SllLeoneMember', "702-SGD":'Valyuta_702SgdSingapurskijDollarMember', "704-VND":'Valyuta_704VndDongMember', "706-SOS":'Valyuta_706SosSomalijskijSHillingMember', "710-ZAR":'Valyuta_710ZarRendMember', "728-SSP":'Valyuta_728SspYUzhnosudanskijFuntMember', "748-SZL":'Valyuta_748SzlLilangeniMember', "752-SEK":'Valyuta_752SekSHvedskayaKronaMember', "756-CHF":'Valyuta_756ChfSHvejczarskijFrankMember', "760-SYP":'Valyuta_760SypSirijskijFuntMember', "764-THB":'Valyuta_764ThbBatMember', "776-TOP":'Valyuta_776TopPaangaMember', "780-TTD":'Valyuta_780TtdDollarTrinidadaITobagoMember', "784-AED":'Valyuta_784AedDirxamOaeMember', "788-TND":'Valyuta_788TndTunisskijDinarMember', "800-UGX":'Valyuta_800UgxUgandijskijSHillingMember', "807-MKD":'Valyuta_807MkdDenarMember', "818-EGP":'Valyuta_818EgpEgipetskijFuntMember', "826-GBP":'Valyuta_826GbpFuntSterlingovMember', "834-TZS":'Valyuta_834TzsTanzanijskijSHillingMember', "840-USD":'Valyuta_840UsdDollarSshaMember', "858-UYU":'Valyuta_858UyuUrugvajskoePesoMember', "860-UZS":'Valyuta_860UzsUzbekskijSumMember', "882-WST":'Valyuta_882WstTalaMember', "886-YER":'Valyuta_886YerJemenskijRialMember', "901-TWD":'Valyuta_901TwdNovyjTajvanskijDollarMember', "931-CUC":'Valyuta_931CucKonvertiruemoePesoMember', "932-ZWL":'Valyuta_932ZwlDollarZimbabveMember', "934-TMT":'Valyuta_934TmtNovyjTurkmenskijManatMember', "936-GHS":'Valyuta_936GhsGanskijSediMember', "937-VEF":'Valyuta_937VefBolivarMember', "938-SDG":'Valyuta_938SdgSudanskijFuntMember', "940-UYI":'Valyuta_940UyiUrugvajskoePesoVIndeksirovannyxEdiniczaxMember', "941-RSD":'Valyuta_941RsdSerbskijDinarMember', "943-MZN":'Valyuta_943MznMozambikskijMetikalMember', "944-AZN":'Valyuta_944AznAzerbajdzhanskijManatMember', "946-RON":'Valyuta_946RonRumynskijLejMember', "949-TRY":'Valyuta_949TryTureczkayaLiraMember', "950-XAF":'Valyuta_950XafFrankKfaVeasMember', "951-XCD":'Valyuta_951XcdVostochnoKaribskijDollarMember', "952-XOF":'Valyuta_952XofFrankKfaVseaoMember', "953-XPF":'Valyuta_953XpfFrankKfpMember', "960-XDR":'Valyuta_960XdrSdrSpeczialnyePravaZaimstvovaniyaMember', "967-ZMW":'Valyuta_967ZmwZambijskayaKvachaMember', "968-SRD":'Valyuta_968SrdSurinamskijDollarMember', "969-MGA":'Valyuta_969MgaMalagasijskijAriariMember', "970-COU":'Valyuta_970CouEdiniczaRealnojStoimostiMember', "971-AFN":'Valyuta_971AfnAfganiMember', "972-TJS":'Valyuta_972TjsSomoniMember', "973-AOA":'Valyuta_973AoaKvanzaMember', "974-BYR":'Valyuta_974ByrBelorusskijRublMember', "975-BGN":'Valyuta_975BgnBolgarskijLevMember', "976-CDF":'Valyuta_976CdfKongolezskijFrankMember', "977-BAM":'Valyuta_977BamKonvertiruemayaMarkaMember', "978-EUR":'Valyuta_978EurEvroMember', "980-UAH":'Valyuta_980UahGrivnaMember', "981-GEL":'Valyuta_981GelLariMember', "985-PLN":'Valyuta_985PlnZlotyjMember', "986-BRL":'Valyuta_986BrlBrazilskijRealMember', "004":'Strana_004AfgAfganistanMember', "008":'Strana_008AlbAlbaniyaMember', "010":'Strana_010AtaAntarktidaMember', "012":'Strana_012DzaAlzhirMember', "016":'Strana_016AsmAmerikanskoeSamoaMember', "020":'Strana_020AndAndorraMember', "024":'Strana_024AgoAngolaMember', "028":'Strana_028AtgAntiguaIBarbudaMember', "031":'Strana_031AzeAzerbajdzhanMember', "032":'Strana_032ArgArgentinaMember', "036":'Strana_036AusAvstraliyaMember', "040":'Strana_040AutAvstriyaMember', "044":'Strana_044BhsBagamyMember', "048":'Strana_048BhrBaxrejnMember', "050":'Strana_050BgdBangladeshMember', "051":'Strana_051ArmArmeniyaMember', "052":'Strana_052BrbBarbadosMember', "056":'Strana_056BelBelgiyaMember', "060":'Strana_060BmuBermudyMember', "064":'Strana_064BtnButanMember', "068":'Strana_068BolBoliviyaMnogonaczionalnoeGosudarstvoMember', "070":'Strana_070BihBosniyaIGerczegovinaMember', "072":'Strana_072BwaBotsvanaMember', "074":'Strana_074BvtOstrovBuveMember', "076":'Strana_076BraBraziliyaMember', "084":'Strana_084BlzBelizMember', "086":'Strana_086IotBritanskayaTerritoriyaVIndijskomOkeaneMember', "090":'Strana_090SlbSolomonovyOstrovaMember', "092":'Strana_092VgbVirginskieOstrovaBritanskieMember', "096":'Strana_096BrnBrunejDarussalamMember', "100":'Strana_100BgrBolgariyaMember', "104":'Strana_104MmrMyanmaMember', "108":'Strana_108BdiBurundiMember', "112":'Strana_112BlrBelarusMember', "116":'Strana_116KhmKambodzhaMember', "120":'Strana_120CmrKamerunMember', "124":'Strana_124CanKanadaMember', "132":'Strana_132CpvKaboVerdeMember', "136":'Strana_136CymOstrovaKajmanMember', "140":'Strana_140CafCZentralnoAfrikanskayaRespublikaMember', "144":'Strana_144LkaSHriLankaMember', "148":'Strana_148TcdCHadMember', "152":'Strana_152ChlCHiliMember', "156":'Strana_156ChnKitajMember', "158":'Strana_158TwnTajvanKitajMember', "162":'Strana_162CxrOstrovRozhdestvaMember', "166":'Strana_166CckKokosovyeKilingOstrovaMember', "170":'Strana_170ColKolumbiyaMember', "174":'Strana_174ComKomoryMember', "175":'Strana_175MytMajottaMember', "178":'Strana_178CogKongoMember', "180":'Strana_180CodKongoDemokraticheskayaRespublikaMember', "184":'Strana_184CokOstrovaKukaMember', "188":'Strana_188CriKostaRikaMember', "191":'Strana_191HrvXorvatiyaMember', "192":'Strana_192CubKubaMember', "196":'Strana_196CypKiprMember', "203":'Strana_203CzeCHeshskayaRespublikaMember', "204":'Strana_204BenBeninMember', "208":'Strana_208DnkDaniyaMember', "212":'Strana_212DmaDominikaMember', "214":'Strana_214DomDominikanskayaRespublikaMember', "218":'Strana_218EcuEkvadorMember', "222":'Strana_222SlvElSalvadorMember', "226":'Strana_226GnqEkvatorialnayaGvineyaMember', "231":'Strana_231EthEfiopiyaMember', "232":'Strana_232EriEritreyaMember', "233":'Strana_233EstEstoniyaMember', "234":'Strana_234FroFarerskieOstrovaMember', "238":'Strana_238FlkFolklendskieOstrovaMalvinskieMember', "239":'Strana_239SgsYUzhnayaDzhordzhiyaIYUzhnyeSandvichevyOstrovaMember', "242":'Strana_242FjiFidzhiMember', "246":'Strana_246FinFinlyandiyaMember', "248":'Strana_248AlaElandskieOstrovaMember', "250":'Strana_250FraFrancziyaMember', "254":'Strana_254GufFranczuzskayaGvianaMember', "258":'Strana_258PyfFranczuzskayaPolineziyaMember', "260":'Strana_260AtfFranczuzskieYUzhnyeTerritoriiMember', "262":'Strana_262DjiDzhibutiMember', "266":'Strana_266GabGabonMember', "268":'Strana_268GeoGruziyaMember', "270":'Strana_270GmbGambiyaMember', "275":'Strana_275PsePalestinaGosudarstvoMember', "276":'Strana_276DeuGermaniyaMember', "288":'Strana_288GhaGanaMember', "292":'Strana_292GibGibraltarMember', "296":'Strana_296KirKiribatiMember', "300":'Strana_300GrcGrecziyaMember', "304":'Strana_304GrlGrenlandiyaMember', "308":'Strana_308GrdGrenadaMember', "312":'Strana_312GlpGvadelupaMember', "316":'Strana_316GumGuamMember', "320":'Strana_320GtmGvatemalaMember', "324":'Strana_324GinGvineyaMember', "328":'Strana_328GuyGajanaMember', "332":'Strana_332HtiGaitiMember', "334":'Strana_334HmdOstrovXerdIOstrovaMakdonaldMember', "336":'Strana_336VatPapskijPrestolGosudarstvoGorodVatikanMember', "340":'Strana_340HndGondurasMember', "344":'Strana_344HkgGonkongMember', "348":'Strana_348HunVengriyaMember', "352":'Strana_352IslIslandiyaMember', "356":'Strana_356IndIndiyaMember', "360":'Strana_360IdnIndoneziyaMember', "364":'Strana_364IrnIranIslamskayaRespublikaMember', "368":'Strana_368IrqIrakMember', "372":'Strana_372IrlIrlandiyaMember', "376":'Strana_376IsrIzrailMember', "380":'Strana_380ItaItaliyaMember', "384":'Strana_384CivKotDIvuarMember', "388":'Strana_388JamYAmajkaMember', "392":'Strana_392JpnYAponiyaMember', "398":'Strana_398KazKazaxstanMember', "400":'Strana_400JorIordaniyaMember', "404":'Strana_404KenKeniyaMember', "408":'Strana_408PrkKoreyaNarodnoDemokraticheskayaRespublikaMember', "410":'Strana_410KorKoreyaRespublikaMember', "414":'Strana_414KwtKuvejtMember', "417":'Strana_417KgzKirgiziyaMember', "418":'Strana_418LaoLaosskayaNarodnoDemokraticheskayaRespublikaMember', "422":'Strana_422LbnLivanMember', "426":'Strana_426LsoLesotoMember', "428":'Strana_428LvaLatviyaMember', "430":'Strana_430LbrLiberiyaMember', "434":'Strana_434LbyLiviyaMember', "438":'Strana_438LieLixtenshtejnMember', "440":'Strana_440LtuLitvaMember', "442":'Strana_442LuxLyuksemburgMember', "446":'Strana_446MacMakaoMember', "450":'Strana_450MdgMadagaskarMember', "454":'Strana_454MwiMalaviMember', "458":'Strana_458MysMalajziyaMember', "462":'Strana_462MdvMaldivyMember', "466":'Strana_466MliMaliMember', "470":'Strana_470MltMaltaMember', "474":'Strana_474MtqMartinikaMember', "478":'Strana_478MrtMavritaniyaMember', "480":'Strana_480MusMavrikijMember', "484":'Strana_484MexMeksikaMember', "492":'Strana_492McoMonakoMember', "496":'Strana_496MngMongoliyaMember', "498":'Strana_498MdaMoldovaRespublikaMember', "499":'Strana_499MneCHernogoriyaMember', "500":'Strana_500MsrMontserratMember', "504":'Strana_504MarMarokkoMember', "508":'Strana_508MozMozambikMember', "512":'Strana_512OmnOmanMember', "516":'Strana_516NamNamibiyaMember', "520":'Strana_520NruNauruMember', "524":'Strana_524NplNepalMember', "528":'Strana_528NldNiderlandyMember', "531":'Strana_531CuwKyurasaoMember', "533":'Strana_533AbwArubaMember', "534":'Strana_534SxmSenMartenNiderlandskayaCHastMember', "535":'Strana_535BesBonejrSintEstatiusISabaMember', "540":'Strana_540NclNovayaKaledoniyaMember', "548":'Strana_548VutVanuatuMember', "554":'Strana_554NzlNovayaZelandiyaMember', "558":'Strana_558NicNikaraguaMember', "562":'Strana_562NerNigerMember', "566":'Strana_566NgaNigeriyaMember', "570":'Strana_570NiuNiueMember', "574":'Strana_574NfkOstrovNorfolkMember', "578":'Strana_578NorNorvegiyaMember', "580":'Strana_580MnpSevernyeMarianskieOstrovaMember', "581":'Strana_581UmiMalyeTixookeanskieOtdalennyeOstrovaSoedinennyxSHtatovMember', "583":'Strana_583FsmMikroneziyaFederativnyeSHtatyMember', "584":'Strana_584MhlMarshallovyOstrovaMember', "585":'Strana_585PlwPalauMember', "586":'Strana_586PakPakistanMember', "591":'Strana_591PanPanamaMember', "598":'Strana_598PngPapuaNovayaGvineyaMember', "600":'Strana_600PryParagvajMember', "604":'Strana_604PerPeruMember', "608":'Strana_608PhlFilippinyMember', "612":'Strana_612PcnPitkernMember', "616":'Strana_616PolPolshaMember', "620":'Strana_620PrtPortugaliyaMember', "624":'Strana_624GnbGvineyaBisauMember', "626":'Strana_626TlsTimorLesteMember', "630":'Strana_630PriPuertoRikoMember', "634":'Strana_634QatKatarMember', "638":'Strana_638ReuReyunonMember', "642":'Strana_642RouRumyniyaMember', "643":'Strana_643RusRossiyaMember', "646":'Strana_646RwaRuandaMember', "652":'Strana_652BlmSenBartelemiMember', "654":'Strana_654ShnSvyatayaElenaOstrovVozneseniyaMember', "659":'Strana_659KnaSentKitsINevisMember', "660":'Strana_660AiaAngilyaMember', "662":'Strana_662LcaSentLyusiyaMember', "663":'Strana_663MafSenMartenMember', "666":'Strana_666SpmSenPerIMikelonMember', "670":'Strana_670VctSentVinsentIGrenadinyMember', "674":'Strana_674SmrSanMarinoMember', "678":'Strana_678StpSanTomeIPrinsipiMember', "682":'Strana_682SauSaudovskayaAraviyaMember', "686":'Strana_686SenSenegalMember', "688":'Strana_688SrbSerbiyaMember', "690":'Strana_690SycSejshelyMember', "694":'Strana_694SleSerraLeoneMember', "702":'Strana_702SgpSingapurMember', "703":'Strana_703SvkSlovakiyaMember', "704":'Strana_704VnmVetnamMember', "705":'Strana_705SvnSloveniyaMember', "706":'Strana_706SomSomaliMember', "710":'Strana_710ZafYUzhnayaAfrikaMember', "716":'Strana_716ZweZimbabveMember', "724":'Strana_724EspIspaniyaMember', "728":'Strana_728SsdYUzhnyjSudanMember', "729":'Strana_729SdnSudanMember', "732":'Strana_732EshZapadnayaSaxaraMember', "740":'Strana_740SurSurinamMember', "744":'Strana_744SjmSHpiczbergenIYAnMajenMember', "748":'Strana_748SwzSvazilendMember', "752":'Strana_752SweSHvecziyaMember', "756":'Strana_756CheSHvejczariyaMember', "760":'Strana_760SyrSirijskayaArabskayaRespublikaMember', "762":'Strana_762TjkTadzhikistanMember', "764":'Strana_764ThaTailandMember', "768":'Strana_768TgoTogoMember', "772":'Strana_772TklTokelauMember', "776":'Strana_776TonTongaMember', "780":'Strana_780TtoTrinidadITobagoMember', "784":'Strana_784AreObedinennyeArabskieEmiratyMember', "788":'Strana_788TunTunisMember', "792":'Strana_792TurTurcziyaMember', "795":'Strana_795TkmTurkmeniyaMember', "796":'Strana_796TcaOstrovaTerksIKajkosMember', "798":'Strana_798TuvTuvaluMember', "800":'Strana_800UgaUgandaMember', "804":'Strana_804UkrUkrainaMember', "807":'Strana_807MkdRespublikaMakedoniyaMember', "818":'Strana_818EgyEgipetMember', "826":'Strana_826GbrSoedinennoeKorolevstvoMember', "831":'Strana_831GgyGernsiMember', "832":'Strana_832JeyDzhersiMember', "833":'Strana_833ImnOstrovMenMember', "834":'Strana_834TzaTanzaniyaObedinennayaRespublikaMember', "840":'Strana_840UsaSoedinennyeSHtatyMember', "850":'Strana_850VirVirginskieOstrovaSshaMember', "854":'Strana_854BfaBurkinaFasoMember', "858":'Strana_858UryUrugvajMember', "860":'Strana_860UzbUzbekistanMember', "862":'Strana_862VenVenesuelaMember', "876":'Strana_876WlfUollisIFutunaMember', "882":'Strana_882WsmSamoaMember', "887":'Strana_887YemJemenMember', "894":'Strana_894ZmbZambiyaMember', "895":'Strana_895AbhAbxaziyaMember', "896":'Strana_896OstYUzhnayaOsetiyaMember', "998":'Strana_998Mezhdunarodnaya_organizacziyaMember', "Да ":'DaMember', "Нет ":'NetMember', "BON1":'BON1_obligaczii_emitirovannyeFOIV_RF_i_obligacziiBRMember', "BON2":'BON2_obligaczii_emitir_OIVsubektovRF_i_municzobrazovanijMember', "BON3":'BON3_obligaczii_KO_rezidentovMember', "BON4":'BON4_obligaczii_prochix_rezidentovMember', "BON5":'BON5_obligacziiingosudarstv_iobligaczii_inczentrbankovMember', "BON6":'BON6_obligacziibankov_nerezidentovMember', "BON7":'BON7_obligacziiprochixnerezidentovMember', "DS1":'DS1_depozitnyesertifikatyKOrezidentovMember', "DS2":'DS2_depozitnyesertifikatybankovnerezidentovMember', "SS1":'SS1_sbersertifikatyKOrezidentovMember', "SS2":'SS2_sbersertifikatybankovnerezidentovMember', "SHS1":'SHS1_akcziiKOrezidentov_obyknovennyeMember', "SHS2":'SHS2_akcziiKOrezidentov_privilegirovannyeMember', "SHS3":'SHS3_akcziiprochixrezidentov_obyknovennyeMember', "SHS4":'SHS4_akcziiprochixrezidentov_privilegirovannyeMember', "SHS5":'SHS5_akcziibankov_nerezidentovMember', "SHS6":'SHS6_akcziiprochixnerezidentovMember', "SHS7":'SHS7_pai_doli_investfondov_nerezidentovMember', "SHS8":'SHS8_pai_doli_investfondovrezidentovMember', "BIL1":'BIL1_vekselyaFOIV_RFMember', "BIL2":'BIL2_vekselya_OIVsubektov_RFimuniczipalnyxobrazovanijMember', "BIL3":'BIL3_vekselya_KOrezidentovMember', "BIL4":'BIL4_vekselyaprochixrezidentovMember', "BIL5":'BIL5_vekselya_ingosudarstvaMember', "BIL6":'BIL6_vekselya_bankovnerezidentovMember', "BIL7":'BIL7_vekselya_prochixnerezidentovMember', "DR":'DepozitRaspiskiMember', "CON":'CON_konosamentMember', "WTS":'WTS_skladskoesvidetelstvoMember', "OPN":'OPN_opczionyemitentaMember', "ENC":'ENC_zakladnyeMember', "KSU":'KSU_kliringovyjsertifikatuchastiyaMember', "ISU":'ISU_ipotechnyesertifikatyuchastiyaMember', "BR – брокерская":'BR_brokerskayaMember', "OWN – собственная":'OWN_sobstvennayaMember', "АМ – доверительное управление":'AM_doveritelnoeUpravlenieMember', "BS – договор купли-продажи":'BS_dogovorKupliProdazhiMember', "REPO – договор репо":'REPO_dogovorRepoMember', "EXCHANGE – договор мены":'EXCHANGE_dogovorMenyMember', "LOAN – договор займа":'LOAN_dogovorZajmaMember', "SWAP – своп договор":'SWAP_svopDogovorMember', "OPTION – опционный договор":'OPTION_opczionnyjDogovorMember', "FORWARD – форвардный договор":'FORWARD_forvardnyjDogovorMember', "OTHER – иное":'OTHER_inoe_Rek_vneb_sdMember', "NEW – заключение сделки":'NEW_zaklyuchenieCdelkiMember', "CHANGE – изменение условий по сделке":'CHANGE_izmenenieUslovijPoSdelkeMember', "EXECUTION – полное досрочное исполнение требований и обязательств по сделке":'EXECUTION_PolnDosrochnIspolnenTrebIObyazPoSdelkeMember', "FAILURE – неисполнение обязательств по сделке":'FAILURE_NeispolnenieObyazatelstvPoSdelkeMember', "CANCEL – отмена сделки":'CANCEL_OtmenaSdelkiMember', "DVP – поставка против платежа":'DVP_PostavkaProtivPlatezhaMember', "FREE – поставка свободно от платежа":'FREE_PostavkaSvobodnoOtPlatezhaMember', "P – поставочный":'P_postavochnyjMember', "C – расчетный":'C_raschetnyjMember', "U – не определен в момент заключения сделки и неизвестен на отчетную дату":'U_NeOpredVMomentZaklSdelkiINeizvNaOtchetDatuMember', "UPDATE – сведения в информационном сообщении о сделке необходимо изменить;":'UPDATE_SvedeVInformSoobshhOSdelkeNeobxIzmenitMember', "DELETE – ранее предоставленное информационное сообщение о сделке является некорректным и его необходимо удалить":'DELETE_RaneePredInfSoobshhOsdelkeYAvlNekEgoNeobxUdalitMember', "1 – идентификатор государственной корпорации «Банк развития и внешнеэкономической деятельности (Внешэкономбанк)»":'IDgosKorporaczii_VneshekonombankMember', "2 – регистрационный номер кредитной организации – резидента":'RegNomerKO_rezidentaMember', "3 – код СВИФТ кредитной организации – нерезидента":'SVIFT_KO_nerezidentaMember', "4 – регистрационный номер, полученный кредитной организацией –нерезидентом в стране места нахождения, – в случае отсутствия у нее кода СВИФТ":'RegNOmerKO_nerezVStraneMestaNaxozhd_Net_SVIFTMember', "5 – ИНН организации-резидента, не являющейся кредитной организацией":'INN_org_rez_ne_yavl_kred_org_Rek_kl_vneb_sdINNMember', "6 – код иностранной организации (КИО) для организации – нерезидента, не являющейся кредитной организацией":'KIO_organizNerezNeYAvlKOMember', "7 – регистрационный номер организации-нерезидента, не являющейся кредитной организацией, полученный в стране места нахождения, – в случае отсутствия у нее КИО":'RegNomerOrgNerez_neYAvlKO_poluchVstraneNaxozhd_netKIOMember', "8 – идентификатор Международного инвестиционного банка":'IDMezhdunarInvestBankaMember', "9 – идентификатор физического лица":'IDfizicheskogoLiczaMember', "9 – уникальный код клиента во внутреннем учете отчитывающейся организации":'UnikalnyjKodKlientaVoVnutrennemUcheteOtchityvayushhejsyaOrganizacziiMember', "E1 – акции":'E1_akcziiMember', "E2 – паи":'E2_paiMember', "E3 – депозитарные расписки на акции":'E3_DepozitRaspiskiNaAkcziimember', "E4 – индекс долевых инструментов":'E4_IndeksDolevInstrumentovMember', "E5 – корзина долевых инструментов":'E5_KorzinaDolevInstrumentovMember', "D1 – облигации":'D1_obligacziiMember', "D2 – процентные ставки":'D2_proczentnyeStavkiMember', "D3 – индекс долговых инструментов":'D3_IndeksDolgovyxInstrumentovMember', "D4 – корзина долговых инструментов":'D4_KorzinaDolgovyxInstrumentovMember', "D5 – кредитное событие":'D5_KreditnoeSobytieMember', "C1 – товары (за исключением драгоценных металлов)":'C1_Tovary_zaIsklDragMetallovMember', "C2 – товарный индекс":'C2_TovarnyjIndeksMember', "C3 – корзина товарных активов":'C3_KorzinaTovarnyxAktivovMember', "С4 – драгоценные металлы":'S4_DragoczennyeMetallymember', "С5 – индекс на драгоценные металлы":'S5_IndeksNaDragoczennyeMetallyMember', "С6 – корзина драгоценных металлов":'S6_KorzinaDragoczennyxMetallovMember', "V1 – валюты":'V1_valyutyMember', "V2 – валютный индекс":'V2_valyutnyjIndeksMember', "V3 – корзина валют":'V3_korzinaValyutMember', "V4 – валюты и процентные ставки":'V4_ValyutyIProczentnyeStavkiMember', "A – договор, являющийся производным финансовым инструментом":'A_DogovorYAvlProizvFinInstrMember', "X – смешанный портфель, корзина неоднородных активов":'X_SmeshPortfel_KorzinaNeodnorAktivovmember', "M – иное.":'M_inoe_Rek_kontr_po_vneb_sdMember', "5 – свопцион":'SvopczionMember', "1 – валютный форвард":'ValyutnyjForvardMember', "2 – валютный своп":'ValyutnyjSvopMember', "3 – валютный опцион":'ValyutnyjOpczionMember', "4 – кредитно-дефолтный своп":'KreditnoDefoltnyjSvopMember', "6 – валютно-процентный своп":'ValyutnoProczentnyjSvopMember', "7 – сделка фиксации минимума, максимума, минимума и максимума процентной ставки (cap/floor/collar)":'SdelkafiksacziiMinMaksiMinimaks_proczentnojstavkiMember', "8 – процентный своп":'ProczentnyjsvopMember', "9 – процентный форвард":'ProczentnyjForvardMember', "10 – товарный форвард":'TovarnyjForvardMember', "11 – сделка фиксации минимума, максимума, минимума и максимума цены на товар":'SdelkafiksacziiMinMaksiMinimaks_czenynatovarMember', "12 – товарный своп":'TovarnyjsvopMember', "13 – товарный опцион":'TovarnyjopczionMember', "14 – товарный свопцион":'TovarnyjsvopczionMember', "15 – иной форвард":'InojforvardMember', "16 – иной опцион":'InojopczionMember', "17 – иной своп":'InojsvopMember', "18 – иное":'Inoe_Inf_o_vl_reest_czen_bumMember', "1 – стороной, не исполнившей обязательства, является отчитывающаяся организация":'OtchitOrganizacziyaMember', "2 – стороной, не исполнившей обязательства, является контрагент по сделке":'KontragentPoSdelkeMember', "3 – обе стороны не исполнили обязательства по сделке":'ObeStoronyMember', "4 – стороной, не исполнившей обязательства, является третья сторона":'TretyaStoronaMember', "999":'Liczo_bez_grazhdanstvaMember', "B – покупка":'B_pokupkamember', "S – продажа":'S_prodazhamember', "ВНТ – для внутренней ценной бумаги":'Dlya_vnutrennej_czennoj_bumagiMember', "ВНШ – для внешней ценной бумаги":'Dlya_vneshnej_czennoj_bumagiMember', "КИ – для квалифицированных инвесторов;":'KvalificzirovannyjMember', "НИ – для неквалифицированных инвесторов.":'NekvalificzirovannyjMember', "OTHER":'OTHER_fin_instMember', "933-BYN":'Valyuta_933BynBelorusskijRublMember', "930-STN":'Valyuta_930StnDobraMember', "929-MRU":'Valyuta_929MRUMember', "928-VES":'Valyuta_928VESMember'}

NSMAP = {'mem_int': 'http://www.cbr.ru/xbrl/udr/dom/mem-int',
         'xlink': 'http://www.w3.org/1999/xlink',
         'dim_int': 'http://www.cbr.ru/xbrl/udr/dim/dim-int',
         'iso4217': 'http://www.xbrl.org/2003/iso4217',
         'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
         'link': 'http://www.xbrl.org/2003/linkbase',
         'purcb_dic': 'http://www.cbr.ru/xbrl/nso/purcb/dic/purcb-dic',
         'xbrldi': 'http://xbrl.org/2006/xbrldi',
         'xsi_schemaLocation': 'http://xbrl.org/2006/xbrldi http://www.xbrl.org/2006/xbrldi-2006.xsd',
         'xbrli': 'http://www.xbrl.org/2003/instance'}

class Form(QMainWindow):
    def getfile(self,message,ftype):
        return QFileDialog.getOpenFileName(self,message,"./",ftype)

    def gettype(self):
        items = ("месячный", "квартальный", "годовой")
        item, ok = QInputDialog.getItem(self, "Параметры отчета", "тип отчета", items, 0, False)
        if ok and item:
            return(item)
    
    def direct(self,message):
        return QFileDialog.getExistingDirectory(self,message,"./")
    
    def inform(self,message,information):
        return QMessageBox.information(self, message, information)

    def getdate(self,title,message):
        return QInputDialog.getText(self, title, message, text = "ДД.ММ.ГГГГ")

def taxonomy_func(csv_key : str, default : str, deal, taxonomy_dict):
    if deal.get(csv_key) == None:
        return default
    else:
        return taxonomy_dict.get(deal[csv_key],deal[csv_key])

app = QApplication(sys.argv)
explorer = Form()
getCSV = explorer.getfile('Выберите файл со сделками','CSV files (*.csv)')[0]
if getCSV == '':
    sys.exit()
CSV_file = getCSV.split("/")[-1]
getInfSved = explorer.getfile('Выберите файл с информацией и сведением об организации','JSON files (*.json)')[0]
if getInfSved == '':
    getInfSved = os.path.dirname(os.path.abspath(__file__))+'\\inf_and_svedenia_417.json'
'''
getTaxonomy = explorer.getfile('Выберите файл таксономии','Text files (*.txt)')[0]
if getTaxonomy == '':
    getTaxonomy = os.path.dirname(os.path.abspath(__file__))+'\\dict_417.txt'
'''
type_dict = {"месячный":"m","квартальный":"m_q","годовой":"y"}
getType = explorer.gettype()
if getType == None:
    repType = 'm'
else:
    repType = type_dict[getType]
getRepDate = explorer.getdate("Укажите дату","отчетная дата")[0]
if not re.fullmatch(r'\d{2}.\d{2}.\d{4}', str(getRepDate)):
    report_date = str(datetime.datetime.now().date())
else:
    rep_d, rep_m, rep_y = str(getRepDate).split(".")
    report_date = rep_y+'-'+rep_m+'-'+rep_d
print(report_date)
csv_list = []
with open(getCSV) as repFile:  
    reader = csv.DictReader(repFile,delimiter=';')
    for row in reader:
        csv_list.append(row)
with open(getInfSved, encoding="utf-8") as fjson:
    inf_sved = json.load(fjson)
'''
taxonomy_dict = {}
with open(getTaxonomy, 'r') as taxonomy_txt:
    for taxtag in taxonomy_txt:
        taxonomy_dict[taxtag.split(':')[0]] = taxtag.split(':')[1].split('\n')[0]
'''
direction = os.path.dirname(os.path.abspath(__file__))+'\\'
direction = os.path.join(direction, 'temp_XBRL_gen')
if os.path.exists(direction):
    shutil.rmtree(direction)
os.mkdir(direction)

uid_list = []
OGRN = inf_sved["information"]["OGRN"]

count_deal = 0
new_deal = 0
cancel_deal = 0
code_list = []
count_error = 0
count_error_context = 0

last_date = report_date
all_deal_count = len(csv_list)
if all_deal_count >= 100:
    shag = int(all_deal_count/100)
else:
    shag = 1
progress = 0

sg.one_line_progress_meter('', progress, 100, 'Чтение и проверка файла:\n'+CSV_file ,size=(40,20),orientation='h', no_titlebar = True, bar_color=('#00FF00', 'White'),button_color=('White', 'Gray'))

print('Проверка начата')
count_str = 0
unicode_dict = {}
error_list = ""
last_date = report_date
ferror_temp = open(direction+'\\temp_errors_'+CSV_file.split(".")[0]+'.txt','w',encoding='utf-8')
myXBRL_context = open(direction+'\\temp1_XBRL_'+OGRN+'_ep_nso_purcb_'+repType+'_10rd_reestr_0420417_'+report_date.replace("-","")+'.xml','w',encoding='utf-8')
myXBRL_context.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+"\n")
myXBRL_context.write("<xbrli:xbrl xmlns:mem-int=\""+NSMAP["mem_int"]+"\" xmlns:xlink=\""+NSMAP["xlink"]+"\" xmlns:dim-int=\""+NSMAP["dim_int"]+"\" xmlns:iso4217=\""+NSMAP["iso4217"]+"\" xmlns:xsi=\""+NSMAP["xsi"]+"\" xmlns:link=\""+NSMAP["link"]+"\" xmlns:purcb-dic=\""+NSMAP["purcb_dic"]+"\" xmlns:xbrldi=\""+NSMAP["xbrldi"]+"\" xsi:schemaLocation=\""+NSMAP["xsi_schemaLocation"]+"\" xmlns:xbrli=\""+NSMAP["xbrli"]+"\">"+"\n")
myXBRL_context.write("<link:schemaRef xlink:type=\"simple\" xlink:href=\"http://www.cbr.ru/xbrl/nso/purcb/rep/2019-12-31/ep/ep_nso_purcb_"+repType+"_10rd_reestr_0420417.xsd\" />")
myXBRL_purcb = open(direction+'\\temp2_XBRL_'+OGRN+'_ep_nso_purcb_'+repType+'_10rd_reestr_0420417_'+report_date.replace("-","")+'.xml','w',encoding='utf-8')
myXBRL_purcb.write("<xbrli:unit id=\"pure\"><xbrli:measure>xbrli:pure</xbrli:measure></xbrli:unit>"+"\n")
myXBRL_purcb.write("<xbrli:unit id=\"RUB\"><xbrli:measure>iso4217:RUB</xbrli:measure></xbrli:unit>"+"\n") 

if OGRN != '1167746614947':
    ferror_temp.write("Некорректный ОГРН в названии файла\n")
    count_error += 1
if report_date[5:7] in ['01','02','04','05','07','08','10','11']:
    if repType != 'm':
        ferror_temp.write("Месяц не соответсвует точке входа\n")
        count_error += 1
elif report_date[5:7] in ['03','06','09']:
    if repType != 'm_q':
        ferror_temp.write("Месяц не соответсвует точке входа\n")
        count_error += 1
elif report_date[5:7] in ['12']:
    if repType != 'y':
        ferror_temp.write("Месяц не соответсвует точке входа\n")
        count_error += 1
else:
    ferror_temp.write("Некорректно указан месяц в названии файла\n")
for deal in csv_list:
    uid = 'DAB-'+str(uuid.uuid4()).upper()
    uid_list.append(uid)
    count_str += 1
    identifier = OGRN
    period = report_date
    ID_NomeraInformSoobshheniyaOSdelkeTypedName = deal.get("Идентификатор строки",str(count_str))
    if unicode_dict.get(deal.get("Дата заключения сделки")) == None:
        unicode_dict[deal.get("Дата заключения сделки")] = 0
    unicode_dict[deal.get("Дата заключения сделки")] += 1
    try:
        yyyy, mm, dd = str(deal.get("Дата заключения сделки")).split("-")
    except:
        yyyy, mm, dd = ['0000','00','00']
    VnebirzhSdelka = deal.get("Уникальный номер информационного сообщения о сделке",dd+"."+mm+"."+yyyy+"-"+str(unicode_dict[deal.get("Дата заключения сделки")]).rjust(7,"0")+"-001-"+str(deal.get("Код направления сделки",""))[0]+"-001")
    #VnebirzhSdelka = dd+"."+mm+"."+yyyy+"-"+str(unicode_dict[deal.get("Дата заключения сделки")]).rjust(7,"0")+"-001-"+str(deal.get("Код направления сделки",""))[0]+"-001"
    TipVnebirzhSdelkiEnumerator = 'mem-int:'+taxonomy_func('Тип внебиржевой сделки','OWN_sobstvennayaMember',deal,taxonomy_dict)
    Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki = deal.get("Дата заключения сделки","")
    Vid_Dogovora_vnebirzhevoj_sdelkiEnumerator = 'mem-int:'+taxonomy_func('Вид договора','FORWARD_forvardnyjDogovorMember',deal,taxonomy_dict)
    Vid_PFIEnumerator = 'mem-int:'+taxonomy_func('Виды производных финансовых инструментов','ValyutnyjForvardMember',deal,taxonomy_dict)
    Kod_naprav_sdelkiEnumerator = 'mem-int:'+taxonomy_func('Код направления сделки','',deal,taxonomy_dict)
    Vid_Inf_SoobshhEnumerator = 'mem-int:'+taxonomy_func('Вид информационного сообщения о сделке','',deal,taxonomy_dict)
    PlatezhUsloviyaSdelkiEnumerator = 'mem-int:'+taxonomy_func('Платежные условия сделки','C_raschetnyjMember',deal,taxonomy_dict)
    Inform_analiticheskaya_sistema_Rekv_Vnebirzh_Sdelki = deal.get("Информационная аналитическая система","MetaTrader 5")
    Naim_klienta_po_vnebirzhevoj_sdelke_Rek_kl_vneb_sd = deal.get("Наименование клиента","ФЛ")
    Tip_identif_klienta_VnebirzhSdelkaEnumerator = 'mem-int:'+taxonomy_func('Тип идентификатора клиента','UnikalnyjKodKlientaVoVnutrennemUcheteOtchityvayushhejsyaOrganizacziiMember',deal,taxonomy_dict)
    Identifikator_klienta_po_vneb_sdelke_Rek_kl_vneb_sd = deal.get("Идентификатор клиента","")
    Kod_strany_registr_klienta_po_vnebirzh_sdelkeEnumerator = 'mem-int:'+taxonomy_func('Код страны регистрации клиента','Strana_643RusRossiyaMember',deal,taxonomy_dict)
    Naim_kontragenta_po_vnebirzh_sdelke_Rek_kontr_po_vneb_sd = deal.get("Наименование контрагента","ФЛ")
    Tip_identif_kontr_VnebirzhSdelkaEnumerator = 'mem-int:'+taxonomy_func('Тип идентификатора контрагента','UnikalnyjKodKlientaVoVnutrennemUcheteOtchityvayushhejsyaOrganizacziiMember',deal,taxonomy_dict)
    Identr_kontr_po_vneb_sdelke_Rek_kontr_po_vneb_sd = deal.get("Идентификатор контрагента","")
    Kod_strany_registr_kontrag_vnebirzh_sdelkeEnumerator = 'mem-int:'+taxonomy_func('Код страны регистрации контрагента','Strana_643RusRossiyaMember',deal,taxonomy_dict)
    Naim_em_Rek_em_Inf_perv_chast_sdelki = deal.get("Наименование эмитента по 1-й части сделки","")
    ISIN_Rek_em = deal.get("Код финансового инструмента ISIN по 1-й части сделки","")
    Kolvo_fin_instr_Rek_em = deal.get("Количество финансовых инструментов по 1-й части сделки","")
    Tip_bazovogo_aktivaEnumerator = 'mem-int:'+taxonomy_func('Тип базового актива по 1-й части сделки','V1_valyutyMember',deal,taxonomy_dict)
    Bazovyj_aktiv = deal.get("Базовый актив по 1-й части сделки","")
    Tip_FI_vo_VnebSdelke_Kvalif_Nekvalif_Inv_1chsdEnumerator = 'mem-int:'+taxonomy_func('Тип финансового инструмента по 1-й части сделки1','NekvalificzirovannyjMember',deal,taxonomy_dict)
    if deal.get("Код валюты цены по 1-й части сделки") == None:
        Kod_valyuty = ''
    else:
        if not re.fullmatch(r'\d{3}-\w{3}',deal["Код валюты цены по 1-й части сделки"]):
            Kod_valyuty = deal["Код валюты цены по 1-й части сделки"]
            for key in taxonomy_dict:
                if re.fullmatch(deal["Код валюты цены по 1-й части сделки"]+r'-\w{3}', str(key)):
                    Kod_valyuty = taxonomy_dict[key]
        else:
            Kod_valyuty = taxonomy_dict.get(deal["Код валюты цены по 1-й части сделки"],deal["Код валюты цены по 1-й части сделки"])
    Kod_valyuty_vnebirzh_sdelk_Inf_1chast_sdelkEnumerator = 'mem-int:'+Kod_valyuty
    CZena_fin_instrumenta_Rek_em = deal.get("Цена финансового инструмента по 1-й части сделки","")
    Summa_sdelki_v_ediniczax_valyuty_czeny_sdelki_Rek_em = deal.get("Сумма по 1-й части сделки, в единицах валюты цены сделки","")
    Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em = deal.get("Планируемая (фактическая) дата перерегистрации","")
    Data_oplaty_fin_instrumenta_Rek_em = deal.get("Планируемая (фактическая) дата оплаты","")
    Naim_emitenta_Inf_o_vtor_chast_sdelki = deal.get("Наименование эмитента по 2-й части сделки","")
    
    
    if identifier != OGRN:
        error_list += uid + ":\t" + identifier + "\tНекорректный показатель identifier\n"
    if period != last_date:
        error_list += uid + ":\t" + period + "\tНекорректный показатель period\n"
    count_deal += 1
    if not re.fullmatch(r'\d+', ID_NomeraInformSoobshheniyaOSdelkeTypedName):
        error_list += uid + ":\t" + ID_NomeraInformSoobshheniyaOSdelkeTypedName + ":\tНекорректный показатель ID_NomeraInformSoobshheniyaOSdelkeTypedName\n"
    code_list.append(VnebirzhSdelka)
    if not re.fullmatch(r'\d{2}\.\d{2}\.\d{4}-\d{7}-001-[BS]-001', VnebirzhSdelka):
        error_list += uid + ":\t" + VnebirzhSdelka + ":\tНекорректный показатель VnebirzhSdelka\n"
    if TipVnebirzhSdelkiEnumerator != 'mem-int:OWN_sobstvennayaMember':
        error_list += uid + ":\t" + TipVnebirzhSdelkiEnumerator + ":\tНекорректный показатель TipVnebirzhSdelkiEnumerator\n"
    try:
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki) or Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki[0:8] != last_date[0:8]:
            error_list += uid + ":\t" + Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki + ":\tНекорректный показатель Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki\n"
    except:
        error_list += uid + ":\t" + Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki + ":\tНекорректный показатель Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki\n"
    if Vid_Dogovora_vnebirzhevoj_sdelkiEnumerator != 'mem-int:FORWARD_forvardnyjDogovorMember':
        error_list += uid + ":\t" + Vid_Dogovora_vnebirzhevoj_sdelkiEnumerator + ":\tНекорректный показатель Vid_Dogovora_vnebirzhevoj_sdelkiEnumerator\n"
    if Vid_PFIEnumerator != 'mem-int:ValyutnyjForvardMember':
        error_list += uid + ":\t" + Vid_PFIEnumerator + ":\tНекорректный показатель Vid_PFIEnumerator\n"
    if not re.fullmatch(r'mem-int:[BS]_\w+member', Kod_naprav_sdelkiEnumerator):
        error_list += uid + ":\t" + Kod_naprav_sdelkiEnumerator + ":\tНекорректный показатель Kod_naprav_sdelkiEnumerator\n"
    if Vid_Inf_SoobshhEnumerator != 'mem-int:NEW_zaklyuchenieCdelkiMember' and Vid_Inf_SoobshhEnumerator != 'mem-int:CANCEL_OtmenaSdelkiMember':
        error_list += uid + ":\t" + Vid_Inf_SoobshhEnumerator + "\tНекорректный показатель Vid_Inf_SoobshhEnumerator\n"
    else:
        if Vid_Inf_SoobshhEnumerator.split("_")[0] == "mem-int:NEW": new_deal += 1
        if Vid_Inf_SoobshhEnumerator.split("_")[0] == "mem-int:CANCEL": cancel_deal += 1
    if PlatezhUsloviyaSdelkiEnumerator != 'mem-int:C_raschetnyjMember':
        error_list += uid + ":\t" + PlatezhUsloviyaSdelkiEnumerator + ":\tНекорректный показатель PlatezhUsloviyaSdelkiEnumerator\n"
    if Inform_analiticheskaya_sistema_Rekv_Vnebirzh_Sdelki != 'MetaTrader 5':
        error_list += uid + ":\t" + Inform_analiticheskaya_sistema_Rekv_Vnebirzh_Sdelki + ":\tНекорректный показатель Inform_analiticheskaya_sistema_Rekv_Vnebirzh_Sdelki\n"
    if Naim_klienta_po_vnebirzhevoj_sdelke_Rek_kl_vneb_sd != 'ФЛ':
        error_list += uid + ":\t" + Naim_klienta_po_vnebirzhevoj_sdelke_Rek_kl_vneb_sd + ":\tНекорректный показатель Naim_klienta_po_vnebirzhevoj_sdelke_Rek_kl_vneb_sd\n"
    if Tip_identif_klienta_VnebirzhSdelkaEnumerator != 'mem-int:UnikalnyjKodKlientaVoVnutrennemUcheteOtchityvayushhejsyaOrganizacziiMember':
        error_list += uid + ":\t" + Tip_identif_klienta_VnebirzhSdelkaEnumerator + ":\tНекорректный показатель Tip_identif_klienta_VnebirzhSdelkaEnumerator\n"
    if not re.fullmatch(r'AF\d{7}', Identifikator_klienta_po_vneb_sdelke_Rek_kl_vneb_sd):
        error_list += uid + ":\t" + Identifikator_klienta_po_vneb_sdelke_Rek_kl_vneb_sd + ":\tНекорректный показатель Identifikator_klienta_po_vneb_sdelke_Rek_kl_vneb_sd\n"    
    if Kod_strany_registr_klienta_po_vnebirzh_sdelkeEnumerator != 'mem-int:Strana_643RusRossiyaMember':
        error_list += uid + ":\t" + Kod_strany_registr_klienta_po_vnebirzh_sdelkeEnumerator + ":\tНекорректный показатель Kod_strany_registr_klienta_po_vnebirzh_sdelkeEnumerator\n"
    if Naim_kontragenta_po_vnebirzh_sdelke_Rek_kontr_po_vneb_sd != 'ФЛ':
        error_list += uid + ":\t" + Naim_kontragenta_po_vnebirzh_sdelke_Rek_kontr_po_vneb_sd + ":\tНекорректный показатель Naim_kontragenta_po_vnebirzh_sdelke_Rek_kontr_po_vneb_sd\n"
    if Tip_identif_kontr_VnebirzhSdelkaEnumerator != 'mem-int:UnikalnyjKodKlientaVoVnutrennemUcheteOtchityvayushhejsyaOrganizacziiMember':
        error_list += uid + ":\t" + Tip_identif_kontr_VnebirzhSdelkaEnumerator + ":\tНекорректный показатель Tip\n"
    if not re.fullmatch(r'AF\d{7}', Identr_kontr_po_vneb_sdelke_Rek_kontr_po_vneb_sd):
        error_list += uid + ":\t" + Identr_kontr_po_vneb_sdelke_Rek_kontr_po_vneb_sd + ":\tНекорректный показатель Identr_kontr_po_vneb_sdelke_Rek_kontr_po_vneb_sd\n"  
    if Kod_strany_registr_kontrag_vnebirzh_sdelkeEnumerator != 'mem-int:Strana_643RusRossiyaMember':
        error_list += uid + ":\t" + Kod_strany_registr_kontrag_vnebirzh_sdelkeEnumerator + ":\tНекорректный показатель Kod_strany_registr_kontrag_vnebirzh_sdelkeEnumerator\n"
    if Naim_em_Rek_em_Inf_perv_chast_sdelki != "":
        error_list += uid + ":\t" + Naim_em_Rek_em_Inf_perv_chast_sdelki + ":\tНекорректный показатель Naim_em_Rek_em_Inf_perv_chast_sdelki\n"
    if not re.fullmatch(r'[A-Z]{3}/[A-Z]{3}', ISIN_Rek_em):
        error_list += uid + ":\t" + ISIN_Rek_em + ":\tНекорректный показатель ISIN_Rek_em\n"
    if Kolvo_fin_instr_Rek_em == None:
        error_list += uid + ":\t" + Kolvo_fin_instr_Rek_em + ":\tНекорректный показатель Kolvo_fin_instr_Rek_em\n"
    if Tip_bazovogo_aktivaEnumerator != 'mem-int:V1_valyutyMember':
        error_list += uid + ":\t" + Tip_bazovogo_aktivaEnumerator + ":\tНекорректный показатель Tip_bazovogo_aktivaEnumerator\n"
    if not re.fullmatch(r'\d{3}/\d{3}', Bazovyj_aktiv):
        error_list += uid + ":\t" + Bazovyj_aktiv + ":\tНекорректный показатель Bazovyj_aktiv\n"
    if Tip_FI_vo_VnebSdelke_Kvalif_Nekvalif_Inv_1chsdEnumerator != 'mem-int:NekvalificzirovannyjMember':
        error_list += uid + ":\t" + Tip_FI_vo_VnebSdelke_Kvalif_Nekvalif_Inv_1chsdEnumerator + ":\tНекорректный показатель Tip_FI_vo_VnebSdelke_Kvalif_Nekvalif_Inv_1chsdEnumerator\n"
    if not re.fullmatch(r'mem-int:Valyuta_\d{3}\w+Member', Kod_valyuty_vnebirzh_sdelk_Inf_1chast_sdelkEnumerator):
        error_list += uid + ":\t" + Kod_valyuty_vnebirzh_sdelk_Inf_1chast_sdelkEnumerator + ":\tНекорректный показатель Kod_valyuty_vnebirzh_sdelk_Inf_1chast_sdelkEnumerator\n"
    if CZena_fin_instrumenta_Rek_em == None:
        error_list += uid + ":\t" + CZena_fin_instrumenta_Rek_em + ":\tНекорректный показатель CZena_fin_instrumenta_Rek_em\n"
    if Summa_sdelki_v_ediniczax_valyuty_czeny_sdelki_Rek_em == None:
        error_list += uid + ":\t" + Summa_sdelki_v_ediniczax_valyuty_czeny_sdelki_Rek_em + ":\tНекорректный показатель Summa_sdelki_v_ediniczax_valyuty_czeny_sdelki_Rek_em\n"
    try:
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em) or Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em[0:8] != last_date[0:8]:
            error_list += uid + ":\t" + Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em + ":\tНекорректный показатель Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em\n"
    except:
        error_list += uid + ":\t" + Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em + ":\tНекорректный показатель Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em\n"
    try:
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', Data_oplaty_fin_instrumenta_Rek_em) or Data_oplaty_fin_instrumenta_Rek_em[0:8] != last_date[0:8]:
            error_list += uid + ":\t" + Data_oplaty_fin_instrumenta_Rek_em + ":\tНекорректный показатель Data_oplaty_fin_instrumenta_Rek_em\n"
    except:
        error_list += uid + ":\t" + Data_oplaty_fin_instrumenta_Rek_em + ":\tНекорректный показатель Data_oplaty_fin_instrumenta_Rek_em\n"
    if Naim_emitenta_Inf_o_vtor_chast_sdelki != "":
        error_list += uid + ":\t" + Naim_emitenta_Inf_o_vtor_chast_sdelki + ":\tНекорректный показатель Naim_emitenta_Inf_o_vtor_chast_sdelki\n"
    try:
        if VnebirzhSdelka[0:2] != Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki[8:10] or VnebirzhSdelka[3:5] != Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki[5:7] or VnebirzhSdelka[6:10] != Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki[0:4] or VnebirzhSdelka[23] != Kod_naprav_sdelkiEnumerator[8]:
            error_list += uid + ":\tНекорректный уникальный код\n"
    except:
        error_list += uid + ":\tНекорректный уникальный код\n"
    
    if error_list != "":
        count_error_context += 1
        ferror_temp.write(error_list)
        count_error += error_list.count("\n")
    error_list = ""
    
    xml_str = '<xbrli:context id="{context_id}"> <xbrli:entity> <xbrli:identifier scheme="http://www.cbr.ru">{identifier}</xbrli:identifier> </xbrli:entity> <xbrli:period> <xbrli:instant>{period}</xbrli:instant> </xbrli:period>'.format(context_id=uid, identifier=identifier, period=period)
    xml_str += ' <xbrli:scenario> <xbrldi:typedMember dimension="dim-int:ID_NomeraInformSoobshheniyaOSdelkeTaxis"> <dim-int:ID_NomeraInformSoobshheniyaOSdelkeTypedName>{ID_NomeraInformSoobshheniyaOSdelkeTypedName}</dim-int:ID_NomeraInformSoobshheniyaOSdelkeTypedName> </xbrldi:typedMember> </xbrli:scenario> </xbrli:context>'.format(ID_NomeraInformSoobshheniyaOSdelkeTypedName=ID_NomeraInformSoobshheniyaOSdelkeTypedName)
    myXBRL_context.write(xml_str+"\n")

    xml_str = ''
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="VnebirzhSdelka", znachenie=VnebirzhSdelka)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="TipVnebirzhSdelkiEnumerator", znachenie=TipVnebirzhSdelkiEnumerator)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki", znachenie=Data_zaklyucheniya_sdelki_Rekv_Vnebirzh_Sdelki)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Vid_Dogovora_vnebirzhevoj_sdelkiEnumerator", znachenie=Vid_Dogovora_vnebirzhevoj_sdelkiEnumerator)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Kod_naprav_sdelkiEnumerator", znachenie=Kod_naprav_sdelkiEnumerator)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Vid_Inf_SoobshhEnumerator", znachenie=Vid_Inf_SoobshhEnumerator)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="PlatezhUsloviyaSdelkiEnumerator", znachenie=PlatezhUsloviyaSdelkiEnumerator)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Inform_analiticheskaya_sistema_Rekv_Vnebirzh_Sdelki", znachenie=Inform_analiticheskaya_sistema_Rekv_Vnebirzh_Sdelki)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Naim_klienta_po_vnebirzhevoj_sdelke_Rek_kl_vneb_sd", znachenie=Naim_klienta_po_vnebirzhevoj_sdelke_Rek_kl_vneb_sd)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Tip_identif_klienta_VnebirzhSdelkaEnumerator", znachenie=Tip_identif_klienta_VnebirzhSdelkaEnumerator)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Identifikator_klienta_po_vneb_sdelke_Rek_kl_vneb_sd", znachenie=Identifikator_klienta_po_vneb_sdelke_Rek_kl_vneb_sd)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Kod_strany_registr_klienta_po_vnebirzh_sdelkeEnumerator", znachenie=Kod_strany_registr_klienta_po_vnebirzh_sdelkeEnumerator)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Naim_kontragenta_po_vnebirzh_sdelke_Rek_kontr_po_vneb_sd", znachenie=Naim_kontragenta_po_vnebirzh_sdelke_Rek_kontr_po_vneb_sd)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Tip_identif_kontr_VnebirzhSdelkaEnumerator", znachenie=Tip_identif_kontr_VnebirzhSdelkaEnumerator)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Identr_kontr_po_vneb_sdelke_Rek_kontr_po_vneb_sd", znachenie=Identr_kontr_po_vneb_sdelke_Rek_kontr_po_vneb_sd)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Kod_strany_registr_kontrag_vnebirzh_sdelkeEnumerator", znachenie=Kod_strany_registr_kontrag_vnebirzh_sdelkeEnumerator)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Naim_em_Rek_em_Inf_perv_chast_sdelki", znachenie=Naim_em_Rek_em_Inf_perv_chast_sdelki)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="ISIN_Rek_em", znachenie=ISIN_Rek_em)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}" decimals="2" unitRef="RUB">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Kolvo_fin_instr_Rek_em", znachenie=Kolvo_fin_instr_Rek_em)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Tip_bazovogo_aktivaEnumerator", znachenie=Tip_bazovogo_aktivaEnumerator)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Bazovyj_aktiv", znachenie=Bazovyj_aktiv)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Tip_FI_vo_VnebSdelke_Kvalif_Nekvalif_Inv_1chsdEnumerator", znachenie=Tip_FI_vo_VnebSdelke_Kvalif_Nekvalif_Inv_1chsdEnumerator)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Kod_valyuty_vnebirzh_sdelk_Inf_1chast_sdelkEnumerator", znachenie=Kod_valyuty_vnebirzh_sdelk_Inf_1chast_sdelkEnumerator)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}" decimals="2" unitRef="RUB">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="CZena_fin_instrumenta_Rek_em", znachenie=CZena_fin_instrumenta_Rek_em)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}" decimals="2" unitRef="RUB">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Summa_sdelki_v_ediniczax_valyuty_czeny_sdelki_Rek_em", znachenie=Summa_sdelki_v_ediniczax_valyuty_czeny_sdelki_Rek_em)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em", znachenie=Data_pereregistraczii_prav_na_finansovyj_instrument_Rek_em)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Data_oplaty_fin_instrumenta_Rek_em", znachenie=Data_oplaty_fin_instrumenta_Rek_em)
    xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Naim_emitenta_Inf_o_vtor_chast_sdelki", znachenie=Naim_emitenta_Inf_o_vtor_chast_sdelki)
    myXBRL_purcb.write(xml_str+'\n')
    if count_str % shag == 0:
        progress += 1
        sg.one_line_progress_meter('', progress, 100, 'Чтение и проверка файла:\n'+CSV_file ,size=(40,20),orientation='h', no_titlebar = True, bar_color=('#00FF00', 'White'),button_color=('White', 'Gray'))
del csv_list

uid = 'DAB-'+str(uuid.uuid4()).upper()
uid_list.append(uid)
identifier = OGRN
period = report_date
Kod_Okato3 = inf_sved["information"]["OKATO"]
INN_Prof_uch = inf_sved["information"]["INN"]
OGRN_Prof_uch = inf_sved["information"]["OGRN"]
Poln_Naim_Prof_uch = inf_sved["information"]["poln_naim"]
SokrNaim_Prof_uch = inf_sved["information"]["kratk_naim"]
AdresPocht_Prof_uch = inf_sved["information"]["pochta"]
FIOEIO = inf_sved["information"]["FIO_eio"]
Dolzgnostlizapodpotchetnost = inf_sved["information"]["dolzhn_eio"]
Osnispobyaz = inf_sved["information"]["osnov_eio"]
FIOEIOkontr = inf_sved["information"]["FIO_kontr"]
Osnispobyazkontr = inf_sved["information"]["osnov_kontr"]

if identifier != OGRN:
    error_list += uid + ":\t" + identifier + "\tНекорректный показатель identifier\n"
if period != last_date:
    error_list += uid + ":\t" + period + "\tНекорректный показатель period\n"
if Kod_Okato3 != '45286565000':
    error_list += uid + ":\t" + Kod_Okato3 + ":\tНекорректный показатель Kod_Okato3\n"
if INN_Prof_uch != '7708294216':
    error_list += uid + ":\t" + INN_Prof_uch + ":\tНекорректный показатель INN_Prof_uch\n"
if OGRN_Prof_uch != OGRN:
    error_list += uid + ":\t" + OGRN_Prof_uch + ":\tНекорректный показатель OGRN_Prof_uch\n"
if Poln_Naim_Prof_uch != 'Общество с ограниченной ответственностью "Альфа-Форекс"':
    error_list += uid + ":\t" + Poln_Naim_Prof_uch + ":\tНекорректный показатель Poln_Naim_Prof_uch\n"
if SokrNaim_Prof_uch != 'ООО "Альфа-Форекс"':
    error_list += uid + ":\t" + SokrNaim_Prof_uch + ":\tНекорректный показатель SokrNaim_Prof_uch\n"
if AdresPocht_Prof_uch != '107078, Москва г, Маши Порываевой улица, дом № 7, строение 1, этаж 1':
    error_list += uid + ":\t" + AdresPocht_Prof_uch + ":\tНекорректный показатель AdresPocht_Prof_uch\n"
if FIOEIO != 'Николюк Сергей Васильевич' and FIOEIO != 'Лафа Виктория Владимировна':
    error_list += uid + ":\t" + FIOEIO + ":\tНекорректный показатель FIOEIO\n"
if Dolzgnostlizapodpotchetnost != 'Генеральный директор':
    error_list += uid + ":\t" + Dolzgnostlizapodpotchetnost + ":\tНекорректный показатель Dolzgnostlizapodpotchetnost\n"
if not re.fullmatch(r'Решение единственного участника ООО "Альфа-Форекс" от \d{1,2} (?:августа|сентября) \d{4} года', Osnispobyaz):
    error_list += uid + ":\t" + Osnispobyaz + ":\tНекорректный показатель Osnispobyaz\n"
if FIOEIOkontr != 'Лафа Виктория Владимировна' and FIOEIOkontr != 'Козлова Виктория Викторовна':
    error_list += uid + ":\t" + FIOEIOkontr + ":\tНекорректный показатель FIOEIOkontr\n"
if Osnispobyazkontr != 'Приказ № 8 от 18.09.2018г.':
    error_list += uid + ":\t" + Osnispobyazkontr + ":\tНекорректный показатель Osnispobyazkontr\n"

if error_list != "":
    count_error_context += 1
    ferror_temp.write(error_list)
    count_error += error_list.count("\n")
error_list = ""

xml_str = '<xbrli:context id="{context_id}"> <xbrli:entity> <xbrli:identifier scheme="http://www.cbr.ru">{identifier}</xbrli:identifier> </xbrli:entity> <xbrli:period> <xbrli:instant>{period}</xbrli:instant> </xbrli:period>'.format(context_id=uid, identifier=identifier, period=period)
myXBRL_context.write(xml_str+"\n")
                                                                                                              
xml_str = ''
xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="INN_Prof_uch", znachenie=INN_Prof_uch)
xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="OGRN_Prof_uch", znachenie=OGRN_Prof_uch)
xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Poln_Naim_Prof_uch", znachenie=Poln_Naim_Prof_uch)
xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="SokrNaim_Prof_uch", znachenie=SokrNaim_Prof_uch)
xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="AdresPocht_Prof_uch", znachenie=AdresPocht_Prof_uch)
xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Kod_Okato3", znachenie=Kod_Okato3)
xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="FIOEIO", znachenie=FIOEIO)
xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Dolzgnostlizapodpotchetnost", znachenie=Dolzgnostlizapodpotchetnost)
xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Osnispobyaz", znachenie=Osnispobyaz)
xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="FIOEIOkontr", znachenie=FIOEIOkontr)
xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Osnispobyazkontr", znachenie=Osnispobyazkontr)
myXBRL_purcb.write(xml_str+'\n')

uid = 'DAB-'+str(uuid.uuid4()).upper()
uid_list.append(uid)
identifier = OGRN
period = report_date
explicitMember = 'mem-int:'+inf_sved["svedenya"]["rep_417"]["taxonomy"]
LiczoOtvZaPrOblast = inf_sved["svedenya"]["rep_417"]["FIO_otv"]
DolzhLiczaOtvZaPrOblast = inf_sved["svedenya"]["rep_417"]["dolzhn_otv"]
KontInfLiczaOtvZaPrOblast = inf_sved["svedenya"]["rep_417"]["nomer_otv"]
Priznak_Nulevogo_OtchetaEnumerator = 'mem-int:'+taxonomy_dict.get(inf_sved["svedenya"]["rep_417"].get("priznak_null","Нет"),'NetMember')
NaimITrazrabotchika = inf_sved["svedenya"]["rep_417"]["it_razrab"]

if identifier != OGRN:
    error_list += uid + ":\t" + identifier + "\tНекорректный показатель identifier\n"
if period != last_date:
    error_list += uid + ":\t" + period + "\tНекорректный показатель period\n"
if explicitMember != 'mem-int:OKUD0420417Member':
    error_list += uid + ":\t" + explicitMember + ":\tНекорректный показатель explicitMember\n"
if LiczoOtvZaPrOblast != 'Козлова Виктория Викторовна':
    error_list += uid + ":\t" + LiczoOtvZaPrOblast + ":\tНекорректный показатель LiczoOtvZaPrOblast\n"
if DolzhLiczaOtvZaPrOblast != 'Отдел внутреннего учета':
    error_list += uid + ":\t" + DolzhLiczaOtvZaPrOblast + ":\tНекорректный показатель DolzhLiczaOtvZaPrOblast\n"
if not re.fullmatch(r'\d{11}', KontInfLiczaOtvZaPrOblast):
    error_list += uid + ":\t" + KontInfLiczaOtvZaPrOblast + ":\tНекорректный показатель KontInfLiczaOtvZaPrOblast\n"
if NaimITrazrabotchika != 'ООО "ДИБ СИСТЕМС"':
    error_list += uid + ":\t" + NaimITrazrabotchika + ":\tНекорректный показатель NaimITrazrabotchika\n"

if error_list != "":
    count_error_context += 1
    ferror_temp.write(error_list)
    count_error += error_list.count("\n")
error_list = ""

xml_str = '<xbrli:context id="{context_id}"> <xbrli:entity> <xbrli:identifier scheme="http://www.cbr.ru">{identifier}</xbrli:identifier> </xbrli:entity> <xbrli:period> <xbrli:instant>{period}</xbrli:instant> </xbrli:period>'.format(context_id=uid, identifier=identifier, period=period)
xml_str += ' <xbrli:scenario> <xbrldi:explicitMember dimension="dim-int:OKUDAxis">{explicitMember}</xbrldi:explicitMember> </xbrli:scenario> </xbrli:context>'.format(explicitMember=explicitMember)
myXBRL_context.write(xml_str+"\n")

xml_str = ''
xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="LiczoOtvZaPrOblast", znachenie=LiczoOtvZaPrOblast)
xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="DolzhLiczaOtvZaPrOblast", znachenie=DolzhLiczaOtvZaPrOblast)
xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="KontInfLiczaOtvZaPrOblast", znachenie=KontInfLiczaOtvZaPrOblast)
xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="Priznak_Nulevogo_OtchetaEnumerator", znachenie=Priznak_Nulevogo_OtchetaEnumerator)
xml_str += '<purcb-dic:{pokazatel} contextRef="{context_id}">{znachenie}</purcb-dic:{pokazatel}> '.format(context_id=uid, pokazatel="NaimITrazrabotchika", znachenie=NaimITrazrabotchika)
myXBRL_purcb.write(xml_str+'\n')

print('Проверка закончена')
progress = 100
sg.one_line_progress_meter('', progress, 100, 'Чтение и проверка файла:\n'+CSV_file ,size=(40,20),orientation='h', no_titlebar = True, bar_color=('#00FF00', 'White'),button_color=('White', 'Gray'))

myXBRL_context.close()
myXBRL_purcb.write("</xbrli:xbrl>")
myXBRL_purcb.close()
ferror_temp.close()

info = "Всего сделок:\t"+str(count_deal)
info += "\nновых:\t\t"+str(new_deal)
info += "\nотменных:\t"+str(cancel_deal)
info += "\n\nОшибок:\t"+str(count_error)
info += "\nв "+str(count_error_context)+" контекстах."
if len(code_list) != len(set(code_list)):
    info += "\n\nНЕуникальные коды!!!"
if len(uid_list) != len(set(uid_list)):
    info += "\n\nНЕуникальные UID!!!"
explorer.inform('Результат проверки',info)


result_dir = explorer.direct("Укажите путь для сохранения XBRL")+'/'
if result_dir != '/':
    if (all_deal_count*2+10) >= 100:
        shag = int((all_deal_count*2+10)/100)
    else:
        shag = 1
    progress = 0

    sg.one_line_progress_meter('', progress, 100, 'Запись файла:\n'+'XBRL_'+OGRN+'_ep_nso_purcb_'+repType+'_10rd_reestr_0420417_'+report_date.replace("-","")+'.xml' ,size=(40,20),orientation='h', no_titlebar = True, bar_color=('#00FF00', 'White'),button_color=('White', 'Gray'))
    count_fstr = 0
    
    result_dir = os.path.join(result_dir, 'result_XBRL_gen')
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)
    result_dir += '/'
    if os.path.isfile(result_dir+"info_"+CSV_file.split(".")[0]+".txt"):
        os.remove(result_dir+"info_"+CSV_file.split(".")[0]+".txt")
    if os.path.isfile(result_dir+"errors_"+CSV_file.split(".")[0]+".txt"):
        os.remove(result_dir+"errors_"+CSV_file.split(".")[0]+".txt")
    with open(result_dir+'info_'+CSV_file.split(".")[0]+'.txt','w',encoding='utf-8') as finfo:
        finfo.write(info)
    if count_error != 0:
        shutil.copyfile(direction+"\\temp_errors_"+CSV_file.split(".")[0]+".txt", result_dir+"errors_"+CSV_file.split(".")[0]+".txt")
    with open(result_dir+'XBRL_'+OGRN+'_ep_nso_purcb_'+repType+'_10rd_reestr_0420417_'+report_date.replace("-","")+'.xml','w',encoding='utf-8') as myXBRL:
        with open(direction+'\\temp1_XBRL_'+OGRN+'_ep_nso_purcb_'+repType+'_10rd_reestr_0420417_'+report_date.replace("-","")+'.xml','r',encoding='utf-8') as temp1_XBRL:
            for line in temp1_XBRL:
                count_fstr += 1
                myXBRL.write(line)
                if count_fstr % shag == 0:
                    progress += 1
                    sg.one_line_progress_meter('', progress, 100, 'Запись файла:\n'+'XBRL_'+OGRN+'_ep_nso_purcb_'+repType+'_10rd_reestr_0420417_'+report_date.replace("-","")+'.xml' ,size=(40,20),orientation='h', no_titlebar = True, bar_color=('#00FF00', 'White'),button_color=('White', 'Gray'))
        with open(direction+'\\temp2_XBRL_'+OGRN+'_ep_nso_purcb_'+repType+'_10rd_reestr_0420417_'+report_date.replace("-","")+'.xml','r',encoding='utf-8') as temp2_XBRL:
            for line in temp2_XBRL:
                count_fstr += 1
                myXBRL.write(line)
                if count_fstr % shag == 0:
                    progress += 1
                    sg.one_line_progress_meter('', progress, 100, 'Запись файла:\n'+'XBRL_'+OGRN+'_ep_nso_purcb_'+repType+'_10rd_reestr_0420417_'+report_date.replace("-","")+'.xml' ,size=(40,20),orientation='h', no_titlebar = True, bar_color=('#00FF00', 'White'),button_color=('White', 'Gray'))
    progress = 100
    sg.one_line_progress_meter('', progress, 100, 'Запись файла:\n'+'XBRL_'+OGRN+'_ep_nso_purcb_'+repType+'_10rd_reestr_0420417_'+report_date.replace("-","")+'.xml' ,size=(40,20),orientation='h', no_titlebar = True, bar_color=('#00FF00', 'White'),button_color=('White', 'Gray'))
shutil.rmtree(direction)

explorer.inform('0420417_gen','Выполнено!')
