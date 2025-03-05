using breezynet.Models;
using Microsoft.EntityFrameworkCore;

namespace breezynet
{
    public class BreezyContext(DbContextOptions<BreezyContext> options) : DbContext(options)
    {
        public DbSet<User> Users { get; set; }
        public DbSet<Models.File> Files { get; set; }
        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<User>()
                .HasMany(u => u.Files)             
                .WithOne(f => f.User)              
                .HasForeignKey(f => f.UserId)     
                .OnDelete(DeleteBehavior.Cascade);
        }
    }
}
