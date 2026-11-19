package ghost.diamondrush.fan;
import java.io.*;
import java.util.*;

/** Verified three-layer world records; parser only, not the gameplay engine. */
public final class FanWorldCatalog {
    public static final class Level {
        public final int index,width,height;
        private final byte[][] layers;
        private Level(int index,int width,int height,byte[][] layers){
            this.index=index;this.width=width;this.height=height;this.layers=layers;
        }
        public int tile(int layer,int x,int y){
            if(layer<0||layer>=3||x<0||x>=width||y<0||y>=height)
                throw new IndexOutOfBoundsException("layer/x/y out of bounds");
            return layers[layer][y*width+x]&0xff;
        }
        public byte[] layerCopy(int layer){return layers[layer].clone();}
    }
    public final List<Level> levels;
    private FanWorldCatalog(List<Level> levels){this.levels=Collections.unmodifiableList(levels);}
    public static FanWorldCatalog read(InputStream source)throws IOException{
        DataInputStream in=new DataInputStream(new BufferedInputStream(source));
        int version=in.readUnsignedByte();
        if(version!=1)throw new IOException("Unsupported world version: "+version);
        int count=in.readUnsignedByte();
        if(count<1||count>64)throw new IOException("Invalid level count: "+count);
        List<Level> levels=new ArrayList<Level>();
        for(int n=0;n<count;n++){
            int width=readLE16(in),height=readLE16(in);
            if(width<=0||height<=0||width>256||height>256||width*height>32768)
                throw new IOException("Invalid dimensions: "+width+"x"+height);
            byte[][] layers=new byte[3][];
            for(int i=0;i<3;i++){layers[i]=new byte[width*height];in.readFully(layers[i]);}
            levels.add(new Level(n,width,height,layers));
        }
        if(in.read()!=-1)throw new IOException("Trailing bytes after final level");
        return new FanWorldCatalog(levels);
    }
    private static int readLE16(DataInputStream in)throws IOException{
        int lo=in.readUnsignedByte();return lo|(in.readUnsignedByte()<<8);
    }
}
