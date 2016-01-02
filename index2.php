<?php
	session_start();
?>
<html>
	<head>
	<title> initial page </title>
	</head>
	<body>
		<h1> my page is working </h1>
		<form action="">
			First name<br/>
			<input name="first_name"/>
			<br/>
			Last Name<br/>
			<input name="last_name"/>
			<input type="submit"/>
		</form>
	<?php
		print_r($_GET);
		$_SESSION['first_name']=$_GET['first_name'];
		$_SESSION['last_name']=$_GET['last_name'];
		echo "<br/>";
		echo @$_SESSION['first_name'];
		echo "<br/>";
		echo $_SESSION['last_name'];
	?>
	</body>
</html>