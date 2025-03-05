namespace breezynet.Models
{
    public class File
    {
        public Guid Id { get; set; }
        public string Name { get; set; }
        public string Size { get; set; }
        public string Date { get; set; }
        public Guid UserId { get; set; }
        public virtual User User { get; set; }
    }
}
