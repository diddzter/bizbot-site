<?php
/**
 * Blog index at /blog/ (the "Posts page" configured in Settings -> Reading
 * -- see README). Matches the old site's card-grid listing: thumbnail +
 * title per post, no excerpt/date shown on the cards.
 */
defined( 'ABSPATH' ) || exit;
get_header();
?>

<section class="bb-section">
	<div class="bb-container">
		<h1><?php esc_html_e( 'Blog', 'bizbot' ); ?></h1>

		<div class="bb-post-grid">
			<?php
			while ( have_posts() ) :
				the_post();
				?>
				<a class="bb-post-card" href="<?php the_permalink(); ?>">
					<?php if ( has_post_thumbnail() ) { the_post_thumbnail( 'medium' ); } ?>
					<div class="bb-post-card-body">
						<h3 style="font-size:1rem;margin:0;"><?php the_title(); ?></h3>
					</div>
				</a>
			<?php endwhile; ?>
		</div>

		<?php the_posts_pagination(); ?>
	</div>
</section>

<?php get_footer(); ?>
