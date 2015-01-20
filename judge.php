<html>
<body>
<?php
if $_POST['username'] == 'admin' && $_POST['password'] == '123456'
	echo 'success!';
else
	echo 'failed,sorry,please input the right username or password'
?>
</body>
</html>