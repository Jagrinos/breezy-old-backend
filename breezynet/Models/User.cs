namespace breezynet.Models
{
    public class User
    {
        public Guid Id { get; set; }
        public string Login { get; set; } = "";
        public string Password { get; set; } = "";
        public string Refresh_Token { get; set; } = "";
        public virtual List<File> Files { get; set; } = [];
    }
}
