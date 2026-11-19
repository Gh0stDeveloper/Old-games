package ghost.diamondrush.fan;
import java.io.*;
import java.nio.file.*;
import java.util.*;

/** Isolated fan progression. Never touches the original game's "gamedata". */
public final class FanProgressStore {
    public static final String FILE_NAME="diamond_rush_fan_levels_progress.properties";
    private final File save;
    private final Properties properties=new Properties();
    public FanProgressStore(File internalFilesDirectory) throws IOException {
        if(internalFilesDirectory==null) throw new NullPointerException("internalFilesDirectory");
        if(!internalFilesDirectory.exists() && !internalFilesDirectory.mkdirs())
            throw new IOException("Unable to create app internal directory");
        save=new File(internalFilesDirectory,FILE_NAME);
        properties.setProperty("schema","1");
        if(save.exists()) {
            try(InputStream in=new FileInputStream(save)) { properties.load(in); }
            if(!"1".equals(properties.getProperty("schema"))) throw new IOException("Unrecognized save schema");
        }
    }
    public synchronized boolean isCompleted(String world,int stage) {
        validate(world,stage);
        return "true".equals(properties.getProperty("done."+world+"."+stage));
    }
    public synchronized int unlocked(String world) {
        if(!"lost_city".equals(world)) throw new IllegalArgumentException("Unknown world");
        try {return Math.max(1,Integer.parseInt(properties.getProperty("unlocked."+world,"1")));}
        catch(NumberFormatException e) {return 1;}
    }
    public synchronized void complete(String world,int stage,int stageCount) throws IOException {
        validate(world,stage);
        if(stageCount<1 || stageCount>64 || stage>stageCount)throw new IllegalArgumentException("stageCount");
        Properties proposed=new Properties();
        proposed.putAll(properties);
        proposed.setProperty("done."+world+"."+stage,"true");
        proposed.setProperty("unlocked."+world,
            Integer.toString(Math.min(stageCount,Math.max(unlocked(world),stage+1))));
        persist(proposed);
        properties.clear();
        properties.putAll(proposed);
    }
    private static void validate(String world,int stage){
        if(!"lost_city".equals(world)||stage<1||stage>64)throw new IllegalArgumentException("Unknown fan level");
    }
    private void persist(Properties proposed) throws IOException {
        File temp=new File(save.getParentFile(),FILE_NAME+".tmp");
        try(FileOutputStream out=new FileOutputStream(temp)){
            proposed.store(out,"Diamond Rush Fan Levels");out.getFD().sync();
        }
        try {
            Files.move(temp.toPath(),save.toPath(),StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);
        }catch(AtomicMoveNotSupportedException e){
            Files.move(temp.toPath(),save.toPath(),StandardCopyOption.REPLACE_EXISTING);
        }
    }
}
