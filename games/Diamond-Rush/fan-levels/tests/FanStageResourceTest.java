import ghost.diamondrush.fan.FanWorldCatalog;
import java.io.*;
import java.nio.file.*;
import java.util.zip.*;

/** Test the actual generated 44x30 stage, not just a synthetic map. */
public final class FanStageResourceTest {
    private static void check(boolean ok,String reason){
        if(!ok)throw new AssertionError(reason);
    }
    public static void main(String[] args)throws Exception{
        if(args.length!=2)throw new IllegalArgumentException("stage.bin baseline.apk");
        FanWorldCatalog fan;
        try(InputStream in=new FileInputStream(args[0])){
            fan=FanWorldCatalog.read(in);
        }
        check(fan.levels.size()==1,"fan world must have one stage");
        FanWorldCatalog.Level stage=fan.levels.get(0);
        check(stage.index==0&&stage.width==44&&stage.height==30,"expected Lost City Stage 1 44x30");
        FanWorldCatalog original;
        try(ZipFile archive=new ZipFile(args[1]);
            InputStream in=archive.getInputStream(archive.getEntry("assets/data/w0.bin"))){
            original=FanWorldCatalog.read(in);
        }
        check(original.levels.size()==14,"classic Angkor must have 14 stages");
        FanWorldCatalog.Level base=original.levels.get(2);
        check(base.width==27&&base.height==26,"unexpected baseline Stage 3 dimensions");
        for(int layer=0;layer<3;layer++){
            for(int y=0;y<26;y++){
                for(int x=0;x<27;x++){
                    check(base.tile(layer,x,y)==stage.tile(layer,x,y),
                        "classic core changed at layer="+layer+" x="+x+" y="+y);
                }
            }
        }
        check(stage.tile(0,40,5)==255,"secret area not carved");
        check(stage.tile(2,39,4)==20,"secret 2x2 pattern missing");
        check(stage.tile(2,40,4)==21,"secret 2x2 pattern malformed");
        System.out.println("PASS: real fan w3.bin parsed; 44x30; complete 27x26 classic core unchanged; secret area present");
    }
}
