<?php
defined( 'ABSPATH' ) || exit;
get_header();

while ( have_posts() ) :
	the_post();
	?>
	<article class="bb-section bb-container" style="max-width:760px;">
		<h1><?php the_title(); ?></h1>
		<p class="bb-post-meta"><?php echo esc_html( get_the_date() ); ?></p>
		<div class="bb-post-content">
			<?php the_content(); ?>
		</div>
	</article>
	<?php
endwhile;

get_footer();
